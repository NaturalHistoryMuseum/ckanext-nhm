#!/usr/bin/env python
# encoding: utf-8

import logging
from collections import OrderedDict

import os
import re
from beaker.cache import cache_managers
from webhelpers.html import literal

import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.action as nhm_action
import ckanext.nhm.logic.schema as nhm_schema
from ckan.common import c
from ckan.lib.helpers import url_for
from ckanext.ckanpackager.interfaces import ICkanPackager
from ckanext.contact.interfaces import IContact
from ckanext.doi.interfaces import IDoi
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.nhm.lib.cache import cache_clear_nginx_proxy
from ckanext.nhm.lib.eml import generate_eml
from ckanext.nhm.lib.helpers import (
    resource_view_get_filter_options,
    # NOTE: Need to import a function with a cached decorator so clear caches works
    get_site_statistics,
)
from ckanext.nhm.settings import COLLECTION_CONTACTS
from ckanext.versioned_datastore.interfaces import IVersionedDatastore

get_action = logic.get_action
unflatten = dictization_functions.unflatten
Invalid = p.toolkit.Invalid

log = logging.getLogger(__name__)

# The maximum limit for datastore search
MAX_LIMIT = 5000


class NHMPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    """
    NHM CKAN modifications
        View individual records in a dataset
        Set up NHM (CKAN) model
    """
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IResourceController, inherit=True)
    p.implements(IContact)
    p.implements(IDoi)
    p.implements(IGalleryImage)
    p.implements(ICkanPackager)
    p.implements(IVersionedDatastore)

    ## IConfigurer
    def update_config(self, config):
        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(root_dir, 'ckanext', 'nhm', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])

        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-nhm')

        # Add another public directory for dataset files - this will hopefully be temporary, until DAMS
        p.toolkit.add_public_directory(config, 'files')

    ## IRoutes
    def before_map(self, _map):

        # Add view record
        _map.connect('record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='view')

        # Add dwc view
        _map.connect('dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='dwc')

        # About pages
        _map.connect('about_citation', '/about/citation', controller='ckanext.nhm.controllers.about:AboutController', action='citation')
        _map.connect('about_download', '/about/download', controller='ckanext.nhm.controllers.about:AboutController', action='download')
        _map.connect('about_licensing', '/about/licensing', controller='ckanext.nhm.controllers.about:AboutController', action='licensing')
        _map.connect('about_credits', '/about/credits', controller='ckanext.nhm.controllers.about:AboutController', action='credits')

        # Legal pages
        _map.connect('legal_privacy', '/privacy', controller='ckanext.nhm.controllers.legal:LegalController', action='privacy')
        _map.connect('legal_terms', '/terms-conditions', controller='ckanext.nhm.controllers.legal:LegalController', action='terms')

        # About stats pages
        _map.connect('stats_resources', '/about/statistics/resources', controller='ckanext.nhm.controllers.stats:StatsController', action='resources', ckan_icon='bar-chart')
        _map.connect('stats_contributors', '/about/statistics/contributors', controller='ckanext.nhm.controllers.stats:StatsController', action='contributors', ckan_icon='user')
        _map.connect('stats_records', '/about/statistics/records', controller='ckanext.nhm.controllers.stats:StatsController', action='records', ckan_icon='file-text')

        # Dataset metrics
        _map.connect('dataset_metrics', '/dataset/metrics/{id}', controller='ckanext.nhm.controllers.stats:StatsController', action='dataset_metrics', ckan_icon='bar-chart')
        # NOTE: Access to /datastore/dump/{resource_id} is prevented by NGINX

        object_controller = 'ckanext.nhm.controllers.object:ObjectController'

        _map.connect('object_rdf', '/object/{uuid}.{_format}',
                     controller=object_controller, action='rdf',
                     requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

        # Permalink for specimens - needs to come after the DCAT format dependent
        _map.connect('object_view', '/object/{uuid}',
                     controller=object_controller,
                     action='view')

        # Redirect the old specimen url to the object
        _map.redirect('/specimen/{url:.*}', '/object/{url}')

        # The DCAT plugin breaks these links if enable content negotiation is enabled
        # because it maps to /dataset/{_id} without excluding these actions
        # So we re=add them here to make sure it's working
        _map.connect('add dataset', '/dataset/new', controller='package', action='new')
        _map.connect('/dataset/{action}',
                     controller='package',
                     requirements=dict(action='|'.join([
                         'list',
                         'autocomplete'
                     ])))

        return _map

    # IActions
    def get_actions(self):
        return {
            'record_show': nhm_action.record_show,
            'object_rdf': nhm_action.object_rdf,
            'download_image': nhm_action.download_original_image
        }

    # ITemplateHelpers
    def get_helpers(self):

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

    ## IDatasetForm - CKAN Metadata
    def package_types(self):
        return []

    def is_fallback(self):
        return True

    def create_package_schema(self):
        return nhm_schema.create_package_schema()

    def update_package_schema(self):
        return nhm_schema.update_package_schema()

    def show_package_schema(self):
        return nhm_schema.show_package_schema()

    ## IFacets
    def dataset_facets(self, facets_dict, package_type):

        # Remove organisations and groups
        del facets_dict['organization']
        del facets_dict['groups']

        # Add author facet as the first item
        facets_dict = OrderedDict([('author', 'Authors')] + facets_dict.items())
        facets_dict['creator_user_id'] = 'Users'

        return facets_dict

    ## IPackageController
    def before_search(self, data_dict):
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get('sort', None):
            data_dict['sort'] = u'promoted asc, metadata_modified desc'

        return data_dict

    def before_view(self, pkg_dict):
        """
        Shorten author string
        @param pkg_dict:
        @return: pkg_dict with full list of authors renamed to all_authors, and author field truncated (with HTML!) if necessary
        """
        pkg_dict['all_authors'] = pkg_dict['author']
        pkg_dict['author'] = helpers.dataset_author_truncate(pkg_dict['author'])
        return pkg_dict

    ## IContact
    def mail_alter(self, mail_dict, data_dict):

        # Get the submitted data values
        package_id = data_dict.get('package_id', None)
        package_name = data_dict.get('package_name', None)
        resource_id = data_dict.get('resource_id', None)
        record_id = data_dict.get('record_id', None)

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # URL to provide as link to contact email body
        # Over written by linking to record / resource etc., - see below
        url = None

        # Has the user selected a department
        department = data_dict.get('department', None)

        # Build dictionary of URLs
        urls = {}
        if package_id:
            urls['dataset'] = url_for(controller='package', action='read', id=package_id, qualified=True)
            if resource_id:
                urls['resource'] = url_for(controller='package', action='resource_read', id=package_id, resource_id=resource_id, qualified=True)
                if record_id:
                    urls['record'] = url_for('record', action='view', package_name=package_id, resource_id=resource_id, record_id=record_id, qualified=True)

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
                mail_dict['body'] += '\nDepartment: %s\n' % department
            else:
                mail_dict['recipient_name'] = department
                mail_dict[
                    'body'] += '\nThe contactee has chosen to send this to the {0} department.  Our apologies if this enquiry isn\'t relevant -  please forward this onto data@nhm.ac.uk and we will respond.\nMany thanks, Data Portal team\n\n'.format(
                    department)
                # If we have a package ID, load the package
        elif package_id:
            package_dict = get_action('package_show')(context, {'id': package_id})
            # Load the user - using model rather user_show API which loads all the users packages etc.,
            user_obj = model.User.get(package_dict['creator_user_id'])
            mail_dict['recipient_name'] = user_obj.fullname or user_obj.name
            # Update send to with creator username
            mail_dict['recipient_email'] = user_obj.email
            mail_dict['subject'] = 'Message regarding dataset: %s' % package_dict['title']
            mail_dict[
                'body'] += '\n\nYou have been sent this enquiry via the data portal as you are the author of dataset %s.  Our apologies if this isn\'t relevant - please forward this onto data@nhm.ac.uk and we will respond.\nMany thanks, Data Portal team\n\n' % \
                           package_dict['title'] or package_dict['name']

        for i, url in urls.items():
            mail_dict['body'] += '\n%s: %s' % (i.title(), url)

        # If this is being directed to someone other than @daat@nhm.ac.uk
        # Ensure data@nhm.ac.uk is copied in
        if mail_dict['recipient_email'] != 'data@nhm.ac.uk':
            mail_dict['headers']['cc'] = 'data@nhm.ac.uk'
        return mail_dict

    ## IPackageController
    def after_update(self, context, pkg_dict):

        """
        If this is the specimen resource, clear memcached

        NB: Our version of ckan doesn't have the IResource after_update method
        But updating a resource calls IPackageController.after_update
        @param context:
        @param resource:
        @return:
        """
        for resource in pkg_dict.get('resources', []):
            # If this is the specimen resource ID, clear the collection stats
            if 'id' in resource:
                if resource['id'] in [helpers.get_specimen_resource_id(), helpers.get_indexlot_resource_id()]:
                    log.info('Clearing caches')
                    # Quick and dirty, delete all caches when indexlot or specimens are updated
                    for _cache in cache_managers.values():
                        _cache.clear()

        # Clear the NGINX proxy cache
        cache_clear_nginx_proxy()

    ## IDoi
    def build_metadata(self, pkg_dict, metadata_dict):
        metadata_dict['resource_type'] = pkg_dict.get('dataset_category', None)
        if isinstance(metadata_dict['resource_type'], list) and metadata_dict['resource_type']:
            metadata_dict['resource_type'] = metadata_dict['resource_type'][0]
        contributors = pkg_dict.get('contributors', None)
        if contributors:
            contributors = contributors.split('\n')
            metadata_dict['contributors'] = []
            for contributor in contributors:
                contributor = contributor.replace('\r', '').encode('unicode-escape')
                m = re.search(r'(.*?)\s?\((.*)\)', contributor)
                try:
                    metadata_dict['contributors'].append(
                        {
                            'contributorName': m.group(1),
                            'affiliation': m.group(2),

                        }
                    )
                except AttributeError:
                    metadata_dict['contributors'].append(
                        {
                            'contributorName': contributor
                        }
                    )
        affiliation = pkg_dict.get('affiliation', None)
        if affiliation:
            metadata_dict['affiliation'] = affiliation.encode('unicode-escape')

        return metadata_dict

    @staticmethod
    def metadata_to_xml(xml_dict, metadata):
        if 'contributors' in metadata:
            xml_dict['resource']['contributors'] = {
                'contributor': [],
            }
            for contributor in metadata['contributors']:
                contributor['@contributorType'] = 'Researcher'
                xml_dict['resource']['contributors']['contributor'].append(contributor)

        # FIXME - Datacite 3.1 isn't accepting affiliation in the creator field
        # if 'affiliation' in metadata:
        #     xml_dict['resource']['creators']['creator'][0]['affiliation'] = metadata['affiliation']
        return xml_dict

    # IGalleryImage
    def image_info(self):
        """
        Return info for this plugin
        If resource type is set, only dataset of that type will be available
        :return:
        @rtype: object
        """
        return {
            'title': 'DwC associated media',
            'resource_type': ['dwc', 'csv'],
            'field_type': ['json']
        }

    ## IGalleryImage
    def get_images(self, raw_images, record, data_dict):
        images = []
        title_field = data_dict['resource_view'].get('image_title', None)
        for image in raw_images:
            title = []
            if title_field and title_field in record:
                title.append(record[title_field])
            title.append(image.get('title', image['_id']))

            copyright = '%s<br />&copy; %s' % (
                h.link_to(image['license'], image['license'], target='_blank'),
                image['rightsHolder']
            )
            images.append({
                'href': image['identifier'],
                'thumbnail': image['identifier'].replace('preview', 'thumbnail'),
                'link': h.url_for(
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view',
                    package_name=data_dict['package']['name'],
                    resource_id=data_dict['resource']['id'],
                    record_id=record['_id']
                ),
                'copyright': copyright,
                # Description of image in gallery view
                'description': literal(''.join(['<span>%s</span>' % t for t in title])),
                'title': ' - '.join(title),
                'record_id': record['_id']
            })
        return images

    ## ICkanPackager
    def before_package_request(self, resource_id, package_id, packager_url, request_params):
        '''
        Modify the request params that are about to be sent through to the ckanpackager backend so that an EML param is
        included.

        :param resource_id: the resource id of the resource that is about to be packaged
        :param package_id: the package id of the resource that is about to be packaged
        :param packager_url: the target url for this packaging request
        :param request_params: a dict of parameters that will be sent with the request
        :return: the url and the params as a tuple
        '''
        resource = get_action('resource_show')(None, {'id': resource_id})
        package = get_action('package_show')(None, {'id': package_id})
        if resource.get('datastore_active', False) and resource.get('format', '').lower() == 'dwc':
            # if it's a datastore resource and it's in the DwC format, add EML
            request_params['eml'] = generate_eml(package, resource)
        return packager_url, request_params

    # IVersionedDatastore
    def datastore_modify_data_dict(self, context, data_dict):
        '''
        This function allows overriding of the data dict before datastore_search gets to it. We use
        this opportunity to:

            - remove any of our custom filter options (has image, lat long only etc) and add info
              to the context so that we can pick them up and handle them in datastore_modify_search.
              This is necessary because we define the actual query the filter options use in the
              elasticsearch-dsl lib's objects and therefore need to modify the actual search object
              prior to it being sent to the elasticsearch server.

            - alter the sort if the resource being searched is one of the EMu ones, this allows us
              to enforce a modified by sort order instead of the default and therefore means we can
              show the last changed EMu data first

        :param context: the context dict
        :param data_dict: the data dict
        :return: the modified data dict
        '''
        # remove our custom filters from the filters dict, we'll add them ourselves in the modify
        # search function below
        if u'filters' in data_dict:
            # figure out which options are available for this resource
            resource_show = p.toolkit.get_action(u'resource_show')
            resource = resource_show(context, {u'id': data_dict[u'resource_id']})
            options = resource_view_get_filter_options(resource)
            # we'll store the filters that need applying on the context to avoid repeating our work
            # in the modify search function below
            context[u'option_filters'] = []
            for option in options:
                if option.name in data_dict[u'filters']:
                    # if the option is in the filters, delete it and add it's filter to the context
                    del data_dict[u'filters'][option.name]
                    context[u'option_filters'].append(option.filter_dsl)

        if u'sort' not in data_dict:
            # by default sort the EMu resources by modified so that the latest records are first
            if data_dict['resource_id'] in {helpers.get_specimen_resource_id(),
                                            helpers.get_artefact_resource_id(),
                                            helpers.get_indexlot_resource_id()}:
                data_dict['sort'] = ['modified desc']

        return data_dict

    # IVersionedDatastore
    def datastore_modify_search(self, context, original_data_dict, data_dict, search):
        '''
        This function allows us to modify the search object itself before it is serialised and sent
        to elasticsearch. In this function we currently only do one thing: add the actual
        elasticsearch query DSL for each filter option that was removed in the
        datastore_modify_data_dict above (they are stored in the context so that we can identify
        which ones to add in).

        :param context: the context dict
        :param original_data_dict: the original data dict before any plugins modified it
        :param data_dict: the data dict after all plugins have had a chance to modify it
        :param search: the search object itself
        :return: the modified search object
        '''
        # add our custom filters by looping through the filter dsl objects on the context. These are
        # added by the datastore_modify_data_dict function above if any of our custom filters exist
        for filter_dsl in context.pop(u'option_filters', []):
            # add the filter to the search
            search = search.filter(filter_dsl)
        return search

    # IVersionedDatastore
    def datastore_modify_result(self, context, original_data_dict, data_dict, result):
        # we don't do anything to the result currently
        return result

    # IVersionedDatastore
    def datastore_modify_fields(self, resource_id, mapping, fields):
        '''
        This function allows us to modify the field definitions before they are returned as part of
        the datastore_search action. All we do here is just modify the associatedMedia field if it
        exists to ensure it is treated as an array.

        :param resource_id: the resource id
        :param mapping: the original mapping dict returned by elasticsearch from which the field
                        info has been derived
        :param fields: the fields dict itself
        :return: the fields dict
        '''
        # if we're dealing with one of our EMu backed resources and the associatedMedia field is
        # present set its type to array rather than string (the default). This isn't really
        # necessary from recline's point of view as we override the render of this field's data
        # anyway, but for completeness and correctness we'll do the override
        if resource_id in {helpers.get_specimen_resource_id(), helpers.get_artefact_resource_id(),
                           helpers.get_indexlot_resource_id()}:
            for field_def in fields:
                if field_def['id'] == 'associatedMedia':
                    field_def['type'] = 'array'
                    field_def['sortable'] = False
        return fields

    # IVersionedDatastore
    def datastore_modify_index_doc(self, resource_id, index_doc):
        return index_doc

    # IVersionedDatastore
    def datastore_is_read_only_resource(self, resource_id):
        # we don't want any of the versioned datastore ingestion and indexing code modifying the
        # collections data as we manage it all through the data importer
        return resource_id in {helpers.get_specimen_resource_id(),
                               helpers.get_artefact_resource_id(),
                               helpers.get_indexlot_resource_id()}
