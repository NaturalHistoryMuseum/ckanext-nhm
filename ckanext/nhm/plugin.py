# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
import itertools
import logging
from collections import OrderedDict
from contextlib import suppress
from pathlib import Path

from beaker.cache import cache_managers, cache_regions
from importlib_resources import files

import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.action as nhm_action
import ckanext.nhm.logic.schema as nhm_schema
from ckan.lib.helpers import literal
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit
from ckanext.contact.interfaces import IContact
from ckanext.doi.interfaces import IDoi
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.nhm import routes, cli
from ckanext.nhm.lib.helpers import resource_view_get_filter_options
from ckanext.nhm.lib.mail import (
    create_indexlots_email,
    create_department_email,
    create_package_email,
)
from ckanext.versioned_datastore.interfaces import (
    IVersionedDatastore,
    IVersionedDatastoreDownloads,
)
from ckanext.nhm.lib.utils import get_iiif_status

try:
    from ckanext.status.interfaces import IStatus

    status_available = True
except ImportError:
    status_available = False

log = logging.getLogger(__name__)

MAX_LIMIT = 5000


class NHMPlugin(SingletonPlugin, toolkit.DefaultDatasetForm):
    """
    NHM CKAN modifications.

    View individual records in a dataset, Set up NHM (CKAN) model
    """

    root_dir = files('ckanext.nhm.theme')
    template_dir = root_dir.joinpath('templates')

    implements(interfaces.IActions, inherit=True)
    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IConfigurer, inherit=True)
    implements(interfaces.IDatasetForm, inherit=True)
    implements(interfaces.IFacets, inherit=True)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.IResourceController, inherit=True)
    implements(interfaces.IRoutes, inherit=True)
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(IContact)
    implements(IDoi, inherit=True)
    implements(IGalleryImage)
    implements(IVersionedDatastore, inherit=True)
    implements(interfaces.IClick)
    implements(interfaces.IConfigurable)
    implements(IVersionedDatastoreDownloads, inherit=True)
    if status_available:
        implements(IStatus)

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
            'show_extension_versions': nhm_action.show_extension_versions,
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

        if package_name == 'collection-indexlots':
            create_indexlots_email(mail_dict)
        elif department:
            create_department_email(mail_dict, department)
        elif package_id:
            package = toolkit.get_action('package_show')(context, {'id': package_id})
            create_package_email(mail_dict, package)

        for i, url in urls.items():
            mail_dict['body'] += f'\n{i.title()}: {url}'

        # If this is being directed to someone other than data@nhm.ac.uk ensure
        # data@nhm.ac.uk is copied in
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
            fields.force('scientificName')
            fields.force('family')
            fields.force('typeStatus')
            fields.force('locality')
            fields.force('country')
            fields.force('recordedBy')
            fields.force('catalogNumber')
            fields.force('associatedMediaCount')
            fields.force('preservative')
            fields.force('collectionCode')
            fields.force('year')
            fields.force('month')
            fields.force('day')
            for group in (
                'created',
                'modified',
                'basisOfRecord',
                'institutionCode',
                'associatedMedia.*',
                'barcode',
            ):
                fields.ignore(group)

        return fields

    def datastore_before_convert_basic_query(self, query):
        # see lib.filter_options
        custom_filters = ['_has_image', '_has_lat_long', '_exclude_mineralogy']
        if 'filters' in query:
            for f in custom_filters:
                if f in query['filters']:
                    del query['filters'][f]
        return query

    def datastore_after_convert_basic_query(self, basic_query, multisearch_query):
        basic_filters = basic_query.get('filters')
        if not basic_filters:
            return multisearch_query

        has_image = basic_filters.get('_has_image', False)
        if has_image:
            multisearch_query['filters']['and'].append(
                {'exists': {'fields': ['associatedMedia']}}
            )

        has_lat_long = basic_filters.get('_has_lat_long', False)
        if has_lat_long:
            multisearch_query['filters']['and'].append({'exists': {'geo_field': True}})

        exclude_mineralogy = basic_filters.get('_exclude_mineralogy', False)
        if exclude_mineralogy:
            multisearch_query['filters']['and'].append(
                {
                    'not': [
                        {
                            'string_equals': {
                                'fields': ['collectionCode'],
                                'value': 'min',
                            }
                        }
                    ]
                }
            )

        return multisearch_query

    # IVersionedDatastoreDownloads
    def download_modify_notifier_start_templates(self, plain_template, html_template):
        # completely override the default datastore templates with our own ones
        base = Path(__file__).parent / 'src' / 'download_emails'
        with (base / 'start.txt').open() as p, (base / 'start.html').open() as h:
            return p.read().strip(), h.read().strip()

    def download_modify_notifier_end_templates(self, plain_template, html_template):
        # completely override the default datastore templates with our own ones
        base = Path(__file__).parent / 'src' / 'download_emails'
        with (base / 'end.txt').open() as p, (base / 'end.html').open() as h:
            return p.read().strip(), h.read().strip()

    def download_modify_notifier_error_templates(self, plain_template, html_template):
        # completely override the default datastore templates with our own ones
        base = Path(__file__).parent / 'src' / 'download_emails'
        with (base / 'error.txt').open() as p, (base / 'error.html').open() as h:
            return p.read().strip(), h.read().strip()

    def download_modify_eml(self, eml_dict, query):
        # remove the extra NHM creator caused by the attribution plugin
        creators = []
        for c in eml_dict.get('creator', []):
            user_id = c.get('userId')
            if isinstance(user_id, tuple):
                user_id = user_id[0]
            # there should be only one creator with this ID at this point
            if user_id != '039zvsn29':
                creators.append(c)
        original_nhm = None
        for ix, c in enumerate(creators):
            if c['organizationName'] == toolkit.config.get(
                'ckanext.versioned_datastore.dwc_org_name',
                toolkit.config.get(
                    'ckanext.doi.publisher', toolkit.config.get('ckan.site_title')
                ),
            ):
                original_nhm = ix
                break
        if original_nhm is not None:
            creators[original_nhm]['userId'] = (
                '039zvsn29',
                {'directory': 'https://ror.org/039zvsn29'},
            )
        eml_dict['creator'] = creators
        return eml_dict

    ## IStatus
    def modify_status_reports(self, status_reports):
        iiif_health = get_iiif_status()

        # overall image server status
        if iiif_health['ping'] and iiif_health['status'] == ':)':
            status_text = toolkit._('available')
            status_type = 'good'
        elif iiif_health['ping'] and iiif_health['status'] != ':)':
            status_text = toolkit._('available (issues)')
            status_type = 'ok'
        else:
            status_text = toolkit._('unavailable')
            status_type = 'bad'

        status_reports.append(
            {
                'label': toolkit._('Image server'),
                'value': status_text,
                'group': toolkit._('Images'),
                'help': toolkit._(
                    'The IIIF server provides most of the images in datasets (some are externally hosted)'
                ),
                'state': status_type,
            }
        )

        # specimen images
        if iiif_health['ping'] and iiif_health['specimens'] == ':)':
            status_text = toolkit._('available')
            status_type = 'good'
        else:
            status_text = toolkit._('unavailable')
            status_type = 'bad'

        status_reports.append(
            {
                'label': toolkit._('Specimen images'),
                'value': status_text,
                'group': toolkit._('Images'),
                'help': toolkit._(
                    'Specimen images are a specific subset of images used primarily in the Collection specimens and Index lots datasets'
                ),
                'state': status_type,
            }
        )

        return status_reports
