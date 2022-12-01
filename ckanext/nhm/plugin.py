# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
import itertools
import logging
import os
from collections import OrderedDict
from contextlib import suppress
from pathlib import Path

import ckan.model as model
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.action as nhm_action
import ckanext.nhm.logic.schema as nhm_schema
from beaker.cache import cache_managers, cache_regions
from ckan.lib.helpers import literal
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.ckanpackager.interfaces import ICkanPackager
from ckanext.contact.interfaces import IContact
from ckanext.doi.interfaces import IDoi
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.nhm import routes, cli
from ckanext.nhm.lib.eml import generate_eml
from ckanext.nhm.lib.helpers import resource_view_get_filter_options
from ckanext.nhm.settings import COLLECTION_CONTACTS
from ckanext.versioned_datastore.interfaces import (
    IVersionedDatastore,
    IVersionedDatastoreDownloads,
)

log = logging.getLogger(__name__)

MAX_LIMIT = 5000


class NHMPlugin(SingletonPlugin, toolkit.DefaultDatasetForm):
    """
    NHM CKAN modifications.

    View individual records in a dataset, Set up NHM (CKAN) model
    """

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(root_dir, 'ckanext', 'nhm', 'theme', 'templates')

    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IConfigurer, inherit=True)
    implements(interfaces.IDatasetForm, inherit=True)
    implements(interfaces.IFacets, inherit=True)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.IResourceController, inherit=True)
    implements(interfaces.IRoutes, inherit=True)
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(ICkanPackager)
    implements(IContact)
    implements(IDoi, inherit=True)
    implements(IGalleryImage)
    implements(IVersionedDatastore, inherit=True)
    implements(interfaces.IClick)
    implements(interfaces.IConfigurable)
    implements(IVersionedDatastoreDownloads, inherit=True)

    ## IConfigurable
    def configure(self, config):
        options = {}
        for key, value in config.items():
            if key.startswith('ckanext.nhm.cache.'):
                options[key[18:]] = value

        cache_regions.update({'collection_stats': options})

    ## IActions
    def get_actions(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IActions.get_actions
        '''
        return {
            'record_show': nhm_action.record_show,
            'object_rdf': nhm_action.object_rdf,
            'get_permanent_url': nhm_action.get_permanent_url,
            'user_show': nhm_action.user_show,
            'package_update': nhm_action.package_update,
            'resource_create': nhm_action.resource_create,
            'resource_update': nhm_action.resource_update,
        }

    ## IClick
    def get_commands(self):
        return cli.get_commands()

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    ## IConfigurer
    def update_config(self, config):
        '''
        ..seealso:: ckan.plugins.interfaces.IConfigurer.update_config
        :param config:
        '''
        toolkit.add_template_directory(config, 'theme/templates')
        toolkit.add_public_directory(config, 'theme/public')
        toolkit.add_public_directory(
            config, 'theme/assets/vendor/fontawesome-free-5.14.0-web'
        )
        toolkit.add_resource('theme/assets', 'ckanext-nhm')

        # TODO: 2.9 - double check and then remove this
        # Add another public directory for dataset files - this will hopefully
        # be temporary, until DAMS
        toolkit.add_public_directory(config, 'files')

    ## IDatasetForm
    def package_types(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IDatasetForm.package_types
        '''
        return []

    def is_fallback(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IDatasetForm.is_fallback
        '''
        return True

    def create_package_schema(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IDatasetForm.create_package_schema
        '''
        return nhm_schema.create_package_schema()

    def update_package_schema(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IDatasetForm.update_package_schema
        '''
        return nhm_schema.update_package_schema()

    def show_package_schema(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IDatasetForm.show_package_schema
        '''
        return nhm_schema.show_package_schema()

    ## IFacets
    def dataset_facets(self, facets_dict, package_type):
        '''
        ..seealso:: ckan.plugins.interfaces.IFacets.dataset_facets
        '''

        # Remove organisations and groups
        del facets_dict['organization']
        del facets_dict['groups']

        # Add author facet as the first item
        facets_dict = OrderedDict(
            itertools.chain([('author', 'Authors')], facets_dict.items())
        )
        facets_dict['creator_user_id'] = 'Users'

        return facets_dict

    ## IPackageController
    def before_search(self, data_dict):
        '''
        ..seealso:: ckan.plugins.interfaces.IPackageController.before_search
        '''
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get('sort', None):
            data_dict['sort'] = 'promoted asc, metadata_modified desc'

        return data_dict

    def after_search(self, search_results, search_params):
        '''
        ...seealso:: ckan.plugins.interfaces.IPackageController.after_search
        '''
        # set the collections datasets as top (above other promoted datasets)
        if search_params['sort'].startswith('promoted asc'):
            top_datasets_names = ['collection-specimens', 'collection-indexlots']
            custom_order = []
            other_datasets = []
            for ix, d in enumerate(search_results['results']):
                if d['name'] in top_datasets_names:
                    custom_order.insert(top_datasets_names.index(d['name']), d)
                else:
                    other_datasets.append(d)
                if len(custom_order) == len(top_datasets_names):
                    # to avoid iterating over everything if we've already got them
                    other_datasets += search_results['results'][ix + 1 :]
                    break
            search_results['results'] = custom_order + other_datasets

        return search_results

    def before_view(self, pkg_dict):
        '''
        ..seealso:: ckan.plugins.interfaces.IPackageController.before_view

        :returns: pkg_dict with full list of authors renamed to all_authors, and author
                  field truncated (with HTML!) if necessary

        '''
        pkg_dict['all_authors'] = pkg_dict['author']
        pkg_dict['author'] = helpers.dataset_author_truncate(pkg_dict['author'])
        return pkg_dict

    def after_update(self, context, pkg_dict):
        """
        If this is the specimen resource, clear memcached.

        NB: Our version of ckan doesn't have the IResource after_update method
        But updating a resource calls IPackageController.after_update
        ..seealso:: ckan.plugins.interfaces.IPackageController.after_update
        :param context:
        :param pkg_dict:
        """
        for resource in pkg_dict.get('resources', []):
            # If this is the specimen resource ID, clear the collection stats
            if 'id' in resource:
                if resource['id'] in [
                    helpers.get_specimen_resource_id(),
                    helpers.get_indexlot_resource_id(),
                ]:
                    log.info('Clearing caches')
                    # Quick and dirty, delete all caches when indexlot or specimens
                    # are updated
                    for _cache in cache_managers.values():
                        _cache.clear()

    ## IRoutes
    def before_map(self, _map):
        '''
        ..seealso:: ckan.plugins.interfaces.IRoutes.before_map
        :param _map:
        '''

        # Dataset metrics
        _map.connect(
            'dataset_metrics',
            '/dataset/metrics/{id}',
            controller='ckanext.nhm.controllers.stats:StatsController',
            action='dataset_metrics',
            ckan_icon='bar-chart',
        )
        # NOTE: Access to /datastore/dump/{resource_id} is prevented by NGINX

        # The DCAT plugin breaks these links if enable content negotiation is enabled
        # because it maps to /dataset/{_id} without excluding these actions
        # So we re=add them here to make sure it's working
        # TODO: are these still broken?
        # _map.connect('add dataset', '/dataset/new', controller='dataset',
        #              action='new')
        _map.connect(
            '/dataset/{action}',
            controller='dataset',
            requirements=dict(action='|'.join(['list', 'autocomplete'])),
        )

        return _map

    ## ITemplateHelpers
    def get_helpers(self):
        '''
        ..seealso:: ckan.plugins.interfaces.ITemplateHelpers.get_helpers
        '''

        h = {}

        #  Build a list of helpers from import ckanext.nhm.lib.helpers as nhmhelpers
        for helper in dir(helpers):
            #  Exclude private
            if not helper.startswith('_'):
                func = getattr(helpers, helper)

                #  Ensure it's a function
                if hasattr(func, '__call__'):
                    h[helper] = func
        return h

    ## ICkanPackager
    def before_package_request(
        self, resource_id, package_id, packager_url, request_params
    ):
        """
        Modify the request params that are about to be sent through to the ckanpackager
        backend so that an EML param is included.

        :param resource_id: the resource id of the resource that is about to be packaged
        :param package_id: the package id of the resource that is about to be packaged
        :param packager_url: the target url for this packaging request
        :param request_params: a dict of parameters that will be sent with the request
        :return: the url and the params as a tuple
        """
        resource = toolkit.get_action('resource_show')(None, {'id': resource_id})
        package = toolkit.get_action('package_show')(None, {'id': package_id})
        if (
            resource.get('datastore_active', False)
            and resource.get('format', '').lower() == 'dwc'
        ):
            # if it's a datastore resource and it's in the DwC format, add EML
            request_params['eml'] = generate_eml(package, resource)
        return packager_url, request_params

    ## IContact
    def mail_alter(self, mail_dict, data_dict):
        '''
        ..seealso:: ckanext.contact.interfaces.IContact.mail_alter
        '''

        # Get the submitted data values
        package_id = data_dict.get('package_id', None)
        package_name = data_dict.get('package_name', None)
        resource_id = data_dict.get('resource_id', None)
        record_id = data_dict.get('record_id', None)

        context = {'user': toolkit.c.user or toolkit.c.author}

        # URL to provide as link to contact email body
        # Over written by linking to record / resource etc., - see below
        url = None

        # Has the user selected a department
        department = data_dict.get('department', None)

        # Build dictionary of URLs
        urls = {}
        if package_id:
            urls['dataset'] = toolkit.url_for(
                'dataset.read', id=package_id, qualified=True
            )
            if resource_id:
                urls['resource'] = toolkit.url_for(
                    'resource.read',
                    id=package_id,
                    resource_id=resource_id,
                    qualified=True,
                )
                if record_id:
                    urls['record'] = toolkit.url_for(
                        'record.view',
                        package_name=package_id,
                        resource_id=resource_id,
                        record_id=record_id,
                        qualified=True,
                    )

        # If this is an index lot enquiry, send to entom
        if package_name == 'collection-indexlots':
            mail_dict['subject'] = 'Collection Index lot enquiry'
            mail_dict['recipient_email'] = COLLECTION_CONTACTS['Insects']
            mail_dict['recipient_name'] = 'Insects'
        elif department:
            # User has selected the department
            try:
                mail_dict['recipient_email'] = COLLECTION_CONTACTS[department]
            except KeyError:
                # Other/unknown etc., - so don't set recipient email
                mail_dict['body'] += f'\nDepartment: {department}\n'
            else:
                mail_dict['recipient_name'] = department
                mail_dict['body'] += (
                    f'\nThe contactee has chosen to send this to the {department} '
                    f'department. Our apologies if this enquiry isn\'t '
                    f'relevant - please forward this onto data@nhm.ac.uk '
                    f'and we will respond.\nMany thanks, Data Portal '
                    f'team\n\n'
                )
                # If we have a package ID, load the package
        elif package_id:
            package_dict = toolkit.get_action('package_show')(
                context, {'id': package_id}
            )
            # Load the user - using model rather user_show API which loads all the
            # users packages etc.,
            user_obj = model.User.get(package_dict['creator_user_id'])
            mail_dict['recipient_name'] = user_obj.fullname or user_obj.name
            # Update send to with creator username
            mail_dict['recipient_email'] = user_obj.email
            pkg_title = package_dict['title'] or package_dict['name']
            mail_dict['subject'] = f'Message regarding dataset: {pkg_title}'
            mail_dict['body'] += (
                '\n\nYou have been sent this enquiry via the data portal '
                f'as you are the author of dataset {pkg_title}.  Our apologies '
                'if this isn\'t relevant - please forward this onto '
                'data@nhm.ac.uk and we will respond.\nMany thanks, '
                'Data Portal team\n\n'
            )

        for i, url in urls.items():
            mail_dict['body'] += f'\n{i.title()}: {url}'

        # If this is being directed to someone other than @daat@nhm.ac.uk
        # Ensure data@nhm.ac.uk is copied in
        if mail_dict['recipient_email'] != 'data@nhm.ac.uk':
            mail_dict['headers']['cc'] = 'data@nhm.ac.uk'
        return mail_dict

    ## IDoi
    def build_metadata_dict(self, pkg_dict, metadata_dict, errors):
        '''
        ..seealso:: ckanext.doi.interfaces.IDoi.build_metadata_dict
        '''
        try:
            category = pkg_dict.get('dataset_category', pkg_dict.get('type', 'Dataset'))
            if isinstance(category, list) and len(category) > 0:
                category = category[0]
            elif isinstance(category, list):
                category = 'Dataset'
            metadata_dict['resourceType'] = category
            if 'resourceType' in errors:
                del errors['resourceType']
        except Exception as e:
            errors['resourceType'] = e

        with suppress(Exception):
            affiliation = pkg_dict.get('affiliation', None)
            if affiliation:
                # add the common affiliation to all of the creators in the metadata dict
                authors = metadata_dict.get('creators', [])
                for author in authors:
                    author['affiliations'] = affiliation

        with suppress(Exception):
            descriptions = metadata_dict.get('descriptions', [])
            abstract = pkg_dict.get('notes', None)
            for d in descriptions:
                if d['description'] == abstract:
                    d['descriptionType'] = 'Abstract'

            if 'descriptions' in errors:
                del errors['descriptions']

        return metadata_dict, errors

    ## IGalleryImage
    def image_info(self):
        """
        Return info for this plugin. If resource type is set, only dataset of that type
        will be available.

        ..seealso:: ckanext.gallery.plugins.interfaces.IGalleryImage.image_info
        """
        return {
            'title': 'DwC associated media',
            'resource_type': ['dwc', 'csv', 'tsv'],
            'field_type': ['json'],
        }

    def get_images(self, raw_images, record, data_dict):
        '''
        ..seealso:: ckanext.gallery.plugins.interfaces.IGalleryImage.get_images
        '''
        images = []
        title_field = data_dict['resource_view'].get('image_title', None)
        for image in raw_images:
            title = []
            if title_field and title_field in record:
                title.append(record[title_field])
            title.append(image.get('title', str(image['_id'])))

            copyright = f'{toolkit.h.link_to(image["license"], image["license"], target="_blank")}<br />&copy; {image["rightsHolder"]}'
            image_base_url = image['identifier']
            images.append(
                {
                    'href': f'{image_base_url}/preview',
                    'thumbnail': f'{image_base_url}/thumbnail',
                    'download': f'{image_base_url}/original',
                    'link': toolkit.url_for(
                        'record.view',
                        package_name=data_dict['package']['name'],
                        resource_id=data_dict['resource']['id'],
                        record_id=record['_id'],
                    ),
                    'copyright': copyright,
                    # Description of image in gallery view
                    'description': literal(
                        ''.join([f'<span>{t}</span>' for t in title])
                    ),
                    'title': ' - '.join(map(str, title)),
                    'record_id': record['_id'],
                }
            )
        return images

    ## IVersionedDatastore
    def datastore_modify_data_dict(self, context, data_dict):
        """
        This function allows overriding of the data dict before datastore_search gets to
        it. We use this opportunity to:

            - remove any of our custom filter options (has image, lat long only etc)
            and add info
              to the context so that we can pick them up and handle them in
              datastore_modify_search.
              This is necessary because we define the actual query the filter options
              use in the
              elasticsearch-dsl lib's objects and therefore need to modify the actual
              search object
              prior to it being sent to the elasticsearch server.

            - alter the sort if the resource being searched is one of the EMu ones,
            this allows us
              to enforce a modified by sort order instead of the default and therefore
              means we can
              show the last changed EMu data first

        :param context: the context dict
        :param data_dict: the data dict
        :return: the modified data dict
        """
        # remove our custom filters from the filters dict, we'll add them ourselves in
        # the modify
        # search function below
        if 'filters' in data_dict:
            # figure out which options are available for this resource
            resource_show = toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_view_get_filter_options(resource)
            # we'll store the filters that need applying on the context to avoid
            # repeating our work
            # in the modify search function below
            context['option_filters'] = []
            for option in options:
                if option.name in data_dict['filters']:
                    # if the option is in the filters, delete it and add it's filter
                    # to the context
                    del data_dict['filters'][option.name]
                    context['option_filters'].append(option.filter_dsl)

        if 'sort' not in data_dict:
            # by default sort the EMu resources by modified so that the latest records
            # are first
            if data_dict['resource_id'] in {
                helpers.get_specimen_resource_id(),
                helpers.get_artefact_resource_id(),
                helpers.get_indexlot_resource_id(),
            }:
                data_dict['sort'] = ['modified desc']

        return data_dict

    def datastore_modify_search(self, context, original_data_dict, data_dict, search):
        """
        This function allows us to modify the search object itself before it is
        serialised and sent to elasticsearch. In this function we currently only do one
        thing: add the actual elasticsearch query DSL for each filter option that was
        removed in the datastore_modify_data_dict above (they are stored in the context
        so that we can identify which ones to add in).

        :param context: the context dict
        :param original_data_dict: the original data dict before any plugins modified it
        :param data_dict: the data dict after all plugins have had a chance to modify it
        :param search: the search object itself
        :return: the modified search object
        """
        # add our custom filters by looping through the filter dsl objects on the
        # context. These are
        # added by the datastore_modify_data_dict function above if any of our custom
        # filters exist
        for filter_dsl in context.pop('option_filters', []):
            # add the filter to the search
            search = search.filter(filter_dsl)
        return search

    def datastore_modify_result(self, context, original_data_dict, data_dict, result):
        # if there's the include_urls parameter then include the permanent url of each specimen
        if (
            helpers.get_specimen_resource_id() == data_dict['resource_id']
            and 'include_urls' in original_data_dict
        ):
            for hit in result.hits:
                if 'occurrenceID' in hit.data:
                    hit.data.permanentUrl = toolkit.url_for(
                        'object_view', uuid=hit.data.occurrenceID
                    )

        return result

    def datastore_modify_fields(self, resource_id, mapping, fields):
        """
        This function allows us to modify the field definitions before they are returned
        as part of the datastore_search action. All we do here is just modify the
        associatedMedia field if it exists to ensure it is treated as an array.

        :param resource_id: the resource id
        :param mapping: the original mapping dict returned by elasticsearch from which
        the field
                        info has been derived
        :param fields: the fields dict itself
        :return: the fields dict
        """
        # if we're dealing with one of our EMu backed resources and the
        # associatedMedia field is
        # present set its type to array rather than string (the default). This isn't
        # really
        # necessary from recline's point of view as we override the render of this
        # field's data
        # anyway, but for completeness and correctness we'll do the override
        if resource_id in {
            helpers.get_specimen_resource_id(),
            helpers.get_artefact_resource_id(),
            helpers.get_indexlot_resource_id(),
        }:
            for field_def in fields:
                if field_def['id'] == 'associatedMedia':
                    field_def['type'] = 'array'
                    field_def['sortable'] = False
        return fields

    def datastore_is_read_only_resource(self, resource_id):
        # we don't want any of the versioned datastore ingestion and indexing code
        # modifying the
        # collections data as we manage it all through the data importer
        return resource_id in {
            helpers.get_specimen_resource_id(),
            helpers.get_artefact_resource_id(),
            helpers.get_indexlot_resource_id(),
        }

    def datastore_reserve_slugs(self):
        collection_resource_ids = [
            helpers.get_specimen_resource_id(),
            helpers.get_artefact_resource_id(),
            helpers.get_indexlot_resource_id(),
        ]
        slugs = {
            'collections': dict(resource_ids=collection_resource_ids),
            'everything': dict(resource_ids=[]),
            'specimens': dict(resource_ids=[helpers.get_specimen_resource_id()]),
            'indexlots': dict(resource_ids=[helpers.get_indexlot_resource_id()]),
            'artefacts': dict(resource_ids=[helpers.get_artefact_resource_id()]),
        }
        for collection_code in ('PAL', 'MIN', 'BMNH(E)', 'ZOO', 'BOT'):
            slugs[helpers.get_department(collection_code).lower()] = {
                'resource_ids': collection_resource_ids,
                'query': {
                    'filters': {
                        'and': [
                            {
                                'string_equals': {
                                    'fields': ['collectionCode'],
                                    'value': collection_code,
                                }
                            }
                        ]
                    }
                },
            }
        return slugs

    def datastore_modify_guess_fields(self, resource_ids, fields):
        # if the index lots or specimens collections are in the resource ids list, remove a bunch
        # of groups that we don't care about
        if (
            helpers.get_specimen_resource_id() in resource_ids
            or helpers.get_indexlot_resource_id() in resource_ids
        ):
            fields.force('collectionCode')
            fields.force('typeStatus')
            fields.force('family')
            fields.force('genus')
            for group in (
                'created',
                'modified',
                'basisOfRecord',
                'institutionCode',
                'associatedMedia.*',
            ):
                fields.ignore(group)

        return fields

    # IVersionedDatastoreDownloads
    def download_modify_email_templates(self, plain_template, html_template):
        # completely override the default datastore templates with our own ones
        base = Path(__file__).parent / 'src' / 'download_emails'
        with (base / 'body.txt').open() as p, (base / 'body.html').open() as h:
            return p.read().strip(), h.read().strip()
