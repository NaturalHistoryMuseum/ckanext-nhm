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
from ckanext.datasolr.interfaces import IDataSolr
from ckanext.datastore.interfaces import IDatastore
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
    p.implements(IDatastore)
    p.implements(IDataSolr)
    p.implements(IContact)
    p.implements(IDoi)
    p.implements(IGalleryImage)
    p.implements(ICkanPackager)

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

    ## IDataStore
    def datastore_validate(self, context, data_dict, all_field_ids):
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            # Remove both filter options and field groups from filters
            # These will be handled separately
            for option in resource_view_get_filter_options(resource).keys():
                if option in data_dict['filters']:
                    del data_dict['filters'][option]
        return data_dict

    def datastore_search(self, context, data_dict, all_field_ids, query_dict):
        # Add our options filters
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_view_get_filter_options(resource)
            for o in options:
                if o in data_dict['filters'] and 'true' in data_dict['filters'][o]:
                    if 'sql' in options[o]:
                        query_dict['where'].append(options[o]['sql'])
                elif 'sql_false' in options[o]:
                    query_dict['where'].append(options[o]['sql_false'])

        # Remove old field selection _f from search
        try:
            query_dict['filters'].pop("_f", None)
        except KeyError:
            pass

        # Enhance the full text search, by adding support for double quoted expressions. We leave the
        # full text search query intact (so we benefit from the full text index) and add an additional
        # LIKE statement for each quoted group.
        if 'q' in data_dict and not isinstance(data_dict['q'], dict):
            for match in re.findall('"[^"]+"', data_dict['q']):
                query_dict['where'].append((
                    '"{}"::text LIKE %s'.format(resource['id']),
                    '%' + match[1:-1] + '%'
                ))

        self.enforce_max_limit(query_dict)

        # CKAN's field auto-completion uses full text search on individual fields. This causes
        # problems because of stemming issues, and is quite slow on our data set (even with an
        # appropriate index). We detect this type of queries and replace them with a LIKE query.
        # We also cancel the count query which is not needed for this query and slows things down.
        if 'q' in data_dict and isinstance(data_dict['q'], dict) and len(data_dict['q']) == 1:
            field_name = data_dict['q'].keys()[0]
            if data_dict['fields'] == field_name and data_dict['q'][field_name].endswith(':*'):
                escaped_field_name = '"' + field_name.replace('"', '') + '"'
                value = '%' + data_dict['q'][field_name].replace(':*', '%')

                query_dict = {
                    'distinct': True,
                    'limit': query_dict['limit'],
                    'offset': query_dict['offset'],
                    'sort': [escaped_field_name],
                    'where': [(escaped_field_name + '::citext LIKE %s', value)],
                    'select': [escaped_field_name],
                    'ts_query': '',
                    'count': False
                }
        return query_dict

    def datastore_delete(self, context, data_dict, all_field_ids, query_dict):
        return query_dict

    ## IDataSolr
    def datasolr_validate(self, context, data_dict, field_types):
        return self.datastore_validate(context, data_dict, field_types)

    def datasolr_search(self, context, data_dict, field_types, query_dict):
        # Add our custom filters
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_view_get_filter_options(resource)
            for o in options:
                if o in data_dict['filters'] and 'true' in data_dict['filters'][o] and 'solr' in options[o]:
                    # By default filters are added as {filed_name}:*{value}* but some filters
                    # might require special statements - so add them here
                    query_dict.setdefault('filter_statements', {})[o] = options[o]['solr']
        self.enforce_max_limit(query_dict, 'rows')
        return query_dict

    @staticmethod
    def enforce_max_limit(query_dict, field_name='limit'):
        limit = query_dict.get(field_name, 0)
        if MAX_LIMIT and limit > MAX_LIMIT:
            query_dict[field_name] = MAX_LIMIT

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
