
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import os
import re
import json
import ckan.plugins as p
import ckan.logic as logic
import ckan.model as model
import ckan.lib.helpers as h
from beaker.cache import region_invalidate
from webhelpers.html import literal
from beaker.cache import cache_managers
from ckan.common import c, request
from ckan.lib.helpers import url_for
from itertools import chain
import ckan.lib.navl.dictization_functions as dictization_functions
import ckanext.nhm.logic.action as nhm_action
import ckanext.nhm.logic.schema as nhm_schema
import ckanext.nhm.lib.helpers as helpers
import logging
from jinja2 import Environment

from ckanext.nhm.lib.helpers import (
    resource_view_get_filter_options,
    # NOTE: Need to import a function with a cached decorator so clear caches works
    get_site_statistics,
)

from ckanext.nhm.settings import COLLECTION_CONTACTS
from ckanext.contact.interfaces import IContact
from ckanext.datastore.interfaces import IDatastore
from collections import OrderedDict
from ckanext.doi.interfaces import IDoi
from ckanext.datasolr.interfaces import IDataSolr
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.nhm.lib.cache import cache_clear_nginx_proxy

get_action = logic.get_action
unflatten = dictization_functions.unflatten
Invalid = p.toolkit.Invalid

log = logging.getLogger(__name__)

MAX_LIMIT = 5000


class NHMPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    '''NHM CKAN modifications
        View individual records in a dataset
        Set up NHM (CKAN) model


    '''
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

    ## IConfigurer
    def update_config(self, config):
        '''

        :param config: 

        '''
        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(root_dir, u'ckanext', u'nhm', u'theme', u'templates')
        config[u'extra_template_paths'] = u','.join([template_dir, config.get(u'extra_template_paths', u'')])

        p.toolkit.add_public_directory(config, u'theme/public')
        p.toolkit.add_resource(u'theme/fanstatic', u'ckanext-nhm')

        # Add another public directory for dataset files - this will hopefully be temporary, until DAMS
        p.toolkit.add_public_directory(config, u'files')

    ## IRoutes
    def before_map(self, _map):
        '''

        :param _map: 

        '''

        # Add view record
        _map.connect(u'record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                     controller=u'ckanext.nhm.controllers.record:RecordController',
                     action=u'view')

        # Add dwc view
        _map.connect(u'dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                     controller=u'ckanext.nhm.controllers.record:RecordController',
                     action=u'dwc')

        # About pages
        _map.connect(u'about_citation', '/about/citation', controller=u'ckanext.nhm.controllers.about:AboutController', action=u'citation')
        _map.connect(u'about_download', '/about/download', controller=u'ckanext.nhm.controllers.about:AboutController', action=u'download')
        _map.connect(u'about_licensing', '/about/licensing', controller=u'ckanext.nhm.controllers.about:AboutController', action=u'licensing')
        _map.connect(u'about_credits', '/about/credits', controller=u'ckanext.nhm.controllers.about:AboutController', action=u'credits')

        # Legal pages
        _map.connect(u'legal_privacy', '/privacy', controller=u'ckanext.nhm.controllers.legal:LegalController', action=u'privacy')
        _map.connect(u'legal_terms', '/terms-conditions', controller=u'ckanext.nhm.controllers.legal:LegalController', action=u'terms')

        # About stats pages
        _map.connect(u'stats_resources', '/about/statistics/resources', controller=u'ckanext.nhm.controllers.stats:StatsController', action=u'resources', ckan_icon=u'bar-chart')
        _map.connect(u'stats_contributors', '/about/statistics/contributors', controller=u'ckanext.nhm.controllers.stats:StatsController', action=u'contributors', ckan_icon=u'user')
        _map.connect(u'stats_records', '/about/statistics/records', controller=u'ckanext.nhm.controllers.stats:StatsController', action=u'records', ckan_icon=u'file-text')

        # Dataset metrics
        _map.connect(u'dataset_metrics', '/dataset/metrics/{id}', controller=u'ckanext.nhm.controllers.stats:StatsController', action=u'dataset_metrics', ckan_icon=u'bar-chart')
        # NOTE: Access to /datastore/dump/{resource_id} is prevented by NGINX

        object_controller = u'ckanext.nhm.controllers.object:ObjectController'

        _map.connect(u'object_rdf', '/object/{uuid}.{_format}',
                     controller=object_controller, action=u'rdf',
                     requirements={u'_format': u'xml|rdf|n3|ttl|jsonld'})

        # Permalink for specimens - needs to come after the DCAT format dependent
        _map.connect(u'object_view', '/object/{uuid}',
                     controller=object_controller,
                     action=u'view')

        # Redirect the old specimen url to the object
        _map.redirect('/specimen/{url:.*}', '/object/{url}')

        # The DCAT plugin breaks these links if enable content negotiation is enabled
        # because it maps to /dataset/{_id} without excluding these actions
        # So we re=add them here to make sure it's working
        _map.connect(u'add dataset', '/dataset/new', controller=u'package', action=u'new')
        _map.connect('/dataset/{action}',
                     controller=u'package',
                     requirements=dict(action=u'|'.join([
                         u'list',
                         u'autocomplete'
                     ])))

        return _map

    # IActions
    def get_actions(self):
        ''' '''
        return {
            u'record_show': nhm_action.record_show,
            u'object_rdf': nhm_action.object_rdf,
            u'download_image': nhm_action.download_original_image
        }

    # ITemplateHelpers
    def get_helpers(self):
        ''' '''

        h = {}

        #  Build a list of helpers from import ckanext.nhm.lib.helpers as nhmhelpers
        for helper in dir(helpers):
            #  Exclude private
            if not helper.startswith(u'_'):
                func = getattr(helpers, helper)

                #  Ensure it's a function
                if hasattr(func, u'__call__'):
                    h[helper] = func
        return h

    ## IDatasetForm - CKAN Metadata
    def package_types(self):
        ''' '''
        return []

    def is_fallback(self):
        ''' '''
        return True

    def create_package_schema(self):
        ''' '''
        return nhm_schema.create_package_schema()

    def update_package_schema(self):
        ''' '''
        return nhm_schema.update_package_schema()

    def show_package_schema(self):
        ''' '''
        return nhm_schema.show_package_schema()

    ## IFacets
    def dataset_facets(self, facets_dict, package_type):
        '''

        :param facets_dict: 
        :param package_type: 

        '''

        # Remove organisations and groups
        del facets_dict[u'organization']
        del facets_dict[u'groups']

        # Add author facet as the first item
        facets_dict = OrderedDict([(u'author', u'Authors')] + facets_dict.items())
        facets_dict[u'creator_user_id'] = u'Users'

        return facets_dict

    ## IPackageController
    def before_search(self, data_dict):
        '''

        :param data_dict: 

        '''
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get(u'sort', None):
            data_dict[u'sort'] = u'promoted asc, metadata_modified desc'

        return data_dict

    def before_view(self, pkg_dict):
        '''Shorten author string

        :param pkg_dict: return: pkg_dict with full list of authors renamed to all_authors, and author field truncated (with HTML!) if necessary
        :returns: pkg_dict with full list of authors renamed to all_authors, and author field truncated (with HTML!) if necessary

        '''
        pkg_dict[u'all_authors'] = pkg_dict[u'author']
        pkg_dict[u'author'] = helpers.dataset_author_truncate(pkg_dict[u'author'])
        return pkg_dict

    ## IDataStore
    def datastore_validate(self, context, data_dict, all_field_ids):
        '''

        :param context: 
        :param data_dict: 
        :param all_field_ids: 

        '''
        if u'filters' in data_dict:
            resource_show = p.toolkit.get_action(u'resource_show')
            resource = resource_show(context, {u'id': data_dict[u'resource_id']})
            # Remove both filter options and field groups from filters
            # These will be handled separately
            for option in resource_view_get_filter_options(resource).keys():
                if option in data_dict[u'filters']:
                    del data_dict[u'filters'][option]
        return data_dict

    def datastore_search(self, context, data_dict, all_field_ids, query_dict):
        '''

        :param context: 
        :param data_dict: 
        :param all_field_ids: 
        :param query_dict: 

        '''
        # Add our options filters
        if u'filters' in data_dict:
            resource_show = p.toolkit.get_action(u'resource_show')
            resource = resource_show(context, {u'id': data_dict[u'resource_id']})
            options = resource_view_get_filter_options(resource)
            for o in options:
                if o in data_dict[u'filters'] and u'true' in data_dict[u'filters'][o]:
                    if u'sql' in options[o]:
                        query_dict[u'where'].append(options[o][u'sql'])
                elif u'sql_false' in options[o]:
                    query_dict[u'where'].append(options[o][u'sql_false'])

        # Remove old field selection _f from search
        try:
            query_dict[u'filters'].pop(u'_f', None)
        except KeyError:
            pass

        # Enhance the full text search, by adding support for double quoted expressions. We leave the
        # full text search query intact (so we benefit from the full text index) and add an additional
        # LIKE statement for each quoted group.
        if u'q' in data_dict and not isinstance(data_dict[u'q'], dict):
            for match in re.findall(u'"[^"]+"', data_dict[u'q']):
                query_dict[u'where'].append((
                    u'"{}"::text LIKE %s'.format(resource[u'id']),
                    u'%' + match[1:-1] + u'%'
                ))

        self.enforce_max_limit(query_dict)

        # CKAN's field auto-completion uses full text search on individual fields. This causes
        # problems because of stemming issues, and is quite slow on our data set (even with an
        # appropriate index). We detect this type of queries and replace them with a LIKE query.
        # We also cancel the count query which is not needed for this query and slows things down.
        if u'q' in data_dict and isinstance(data_dict[u'q'], dict) and len(data_dict[u'q']) == 1:
            field_name = data_dict[u'q'].keys()[0]
            if data_dict[u'fields'] == field_name and data_dict[u'q'][field_name].endswith(u':*'):
                escaped_field_name = u'"' + field_name.replace(u'"', u'') + u'"'
                value = u'%' + data_dict[u'q'][field_name].replace(u':*', u'%')

                query_dict = {
                    u'distinct': True,
                    u'limit': query_dict[u'limit'],
                    u'offset': query_dict[u'offset'],
                    u'sort': [escaped_field_name],
                    u'where': [(escaped_field_name + u'::citext LIKE %s', value)],
                    u'select': [escaped_field_name],
                    u'ts_query': u'',
                    u'count': False
                }
        return query_dict

    def datastore_delete(self, context, data_dict, all_field_ids, query_dict):
        '''

        :param context: 
        :param data_dict: 
        :param all_field_ids: 
        :param query_dict: 

        '''
        return query_dict

    ## IDataSolr
    def datasolr_validate(self, context, data_dict, field_types):
        '''

        :param context: 
        :param data_dict: 
        :param field_types: 

        '''
        return self.datastore_validate(context, data_dict, field_types)

    def datasolr_search(self, context, data_dict, field_types, query_dict):
        '''

        :param context: 
        :param data_dict: 
        :param field_types: 
        :param query_dict: 

        '''
        # Add our custom filters
        if u'filters' in data_dict:
            resource_show = p.toolkit.get_action(u'resource_show')
            resource = resource_show(context, {u'id': data_dict[u'resource_id']})
            options = resource_view_get_filter_options(resource)
            for o in options:
                if o in data_dict[u'filters'] and u'true' in data_dict[u'filters'][o] and u'solr' in options[o]:
                    # By default filters are added as {filed_name}:*{value}* but some filters
                    # might require special statements - so add them here
                    query_dict.setdefault(u'filter_statements', {})[o] = options[o][u'solr']
        self.enforce_max_limit(query_dict, u'rows')
        return query_dict

    @staticmethod
    def enforce_max_limit(query_dict, field_name=u'limit'):
        '''

        :param query_dict: 
        :param field_name:  (Default value = u'limit')

        '''
        limit = query_dict.get(field_name, 0)
        if MAX_LIMIT and limit > MAX_LIMIT:
            query_dict[field_name] = MAX_LIMIT

    ## IContact
    def mail_alter(self, mail_dict, data_dict):
        '''

        :param mail_dict: 
        :param data_dict: 

        '''

        # Get the submitted data values
        package_id = data_dict.get(u'package_id', None)
        package_name = data_dict.get(u'package_name', None)
        resource_id = data_dict.get(u'resource_id', None)
        record_id = data_dict.get(u'record_id', None)

        context = {u'model': model, u'session': model.Session, u'user': c.user or c.author}

        # URL to provide as link to contact email body
        # Over written by linking to record / resource etc., - see below
        url = None

        # Has the user selected a department
        department = data_dict.get(u'department', None)

        # Build dictionary of URLs
        urls = {}
        if package_id:
            urls[u'dataset'] = url_for(controller=u'package', action=u'read', id=package_id, qualified=True)
            if resource_id:
                urls[u'resource'] = url_for(controller=u'package', action=u'resource_read', id=package_id, resource_id=resource_id, qualified=True)
                if record_id:
                    urls[u'record'] = url_for(u'record', action=u'view', package_name=package_id, resource_id=resource_id, record_id=record_id, qualified=True)

        # If this is an index lot enquiry, send to entom
        if package_name == u'collection-indexlots':
            mail_dict[u'subject'] = u'Collection Index lot enquiry'
            mail_dict[u'recipient_email'] = COLLECTION_CONTACTS[u'Insects']
            mail_dict[u'recipient_name'] = u'Insects'
        elif department:
            # User has selected the department
            try:
                mail_dict[u'recipient_email'] = COLLECTION_CONTACTS[department]
            except KeyError:
                # Other/unknown etc., - so don't set recipient email
                mail_dict[u'body'] += u'\nDepartment: %s\n' % department
            else:
                mail_dict[u'recipient_name'] = department
                mail_dict[
                    u'body'] += u'\nThe contactee has chosen to send this to the {0} department.  Our apologies if this enquiry isn\'t relevant -  please forward this onto data@nhm.ac.uk and we will respond.\nMany thanks, Data Portal team\n\n'.format(
                    department)
                # If we have a package ID, load the package
        elif package_id:
            package_dict = get_action(u'package_show')(context, {u'id': package_id})
            # Load the user - using model rather user_show API which loads all the users packages etc.,
            user_obj = model.User.get(package_dict[u'creator_user_id'])
            mail_dict[u'recipient_name'] = user_obj.fullname or user_obj.name
            # Update send to with creator username
            mail_dict[u'recipient_email'] = user_obj.email
            mail_dict[u'subject'] = u'Message regarding dataset: %s' % package_dict[u'title']
            mail_dict[
                u'body'] += u'\n\nYou have been sent this enquiry via the data portal as you are the author of dataset %s.  Our apologies if this isn\'t relevant - please forward this onto data@nhm.ac.uk and we will respond.\nMany thanks, Data Portal team\n\n' % \
                           package_dict[u'title'] or package_dict[u'name']

        for i, url in urls.items():
            mail_dict[u'body'] += u'\n%s: %s' % (i.title(), url)

        # If this is being directed to someone other than @daat@nhm.ac.uk
        # Ensure data@nhm.ac.uk is copied in
        if mail_dict[u'recipient_email'] != u'data@nhm.ac.uk':
            mail_dict[u'headers'][u'cc'] = u'data@nhm.ac.uk'
        return mail_dict

    ## IPackageController
    def after_update(self, context, pkg_dict):

        '''If this is the specimen resource, clear memcached
        
        NB: Our version of ckan doesn't have the IResource after_update method
        But updating a resource calls IPackageController.after_update

        :param context: param resource:
        :param pkg_dict: 

        '''
        for resource in pkg_dict.get(u'resources', []):
            # If this is the specimen resource ID, clear the collection stats
            if u'id' in resource:
                if resource[u'id'] in [helpers.get_specimen_resource_id(), helpers.get_indexlot_resource_id()]:
                    log.info(u'Clearing caches')
                    # Quick and dirty, delete all caches when indexlot or specimens are updated
                    for _cache in cache_managers.values():
                        _cache.clear()

        # Clear the NGINX proxy cache
        cache_clear_nginx_proxy()

    ## IDoi
    def build_metadata(self, pkg_dict, metadata_dict):
        '''

        :param pkg_dict: 
        :param metadata_dict: 

        '''
        metadata_dict[u'resource_type'] = pkg_dict.get(u'dataset_category', None)
        if isinstance(metadata_dict[u'resource_type'], list) and metadata_dict[u'resource_type']:
            metadata_dict[u'resource_type'] = metadata_dict[u'resource_type'][0]
        contributors = pkg_dict.get(u'contributors', None)
        if contributors:
            contributors = contributors.split(u'\n')
            metadata_dict[u'contributors'] = []
            for contributor in contributors:
                contributor = contributor.replace(u'\r', u'').encode(u'unicode-escape')
                m = re.search(r'(.*?)\s?\((.*)\)', contributor)
                try:
                    metadata_dict[u'contributors'].append(
                        {
                            u'contributorName': m.group(1),
                            u'affiliation': m.group(2),

                        }
                    )
                except AttributeError:
                    metadata_dict[u'contributors'].append(
                        {
                            u'contributorName': contributor
                        }
                    )
        affiliation = pkg_dict.get(u'affiliation', None)
        if affiliation:
            metadata_dict[u'affiliation'] = affiliation.encode(u'unicode-escape')

        return metadata_dict

    @staticmethod
    def metadata_to_xml(xml_dict, metadata):
        '''

        :param xml_dict: 
        :param metadata: 

        '''
        if u'contributors' in metadata:
            xml_dict[u'resource'][u'contributors'] = {
                u'contributor': [],
            }
            for contributor in metadata[u'contributors']:
                contributor[u'@contributorType'] = u'Researcher'
                xml_dict[u'resource'][u'contributors'][u'contributor'].append(contributor)

        # FIXME - Datacite 3.1 isn't accepting affiliation in the creator field
        # if 'affiliation' in metadata:
        #     xml_dict['resource']['creators']['creator'][0]['affiliation'] = metadata['affiliation']
        return xml_dict

    # IGalleryImage
    def image_info(self):
        '''Return info for this plugin
        If resource type is set, only dataset of that type will be available
        :return:


        '''
        return {
            u'title': u'DwC associated media',
            u'resource_type': [u'dwc', u'csv'],
            u'field_type': [u'json']
        }

    ## IGalleryImage
    def get_images(self, raw_images, record, data_dict):
        '''

        :param raw_images: 
        :param record: 
        :param data_dict: 

        '''
        images = []
        try:
            image_json = json.loads(raw_images)
        except ValueError:
            # Cannot parse field, ignore it
            pass
        except TypeError:
            # Has the wrong image field been selected?
            pass
        else:
            for i in image_json:
                title = []
                for title_field in [u'scientificName', u'catalogNumber']:
                    if record.get(title_field, None):
                        title.append(record.get(title_field))
                copyright = u'%s<br />&copy; %s' % (
                    h.link_to(i[u'license'], i[u'license'], target=u'_blank'),
                    i[u'rightsHolder']
                )
                images.append({
                    u'href': i[u'identifier'],
                    u'thumbnail': i[u'identifier'].replace(u'preview', u'thumbnail'),
                    u'link': h.url_for(
                        controller=u'ckanext.nhm.controllers.record:RecordController',
                        action=u'view',
                        package_name=data_dict[u'package'][u'name'],
                        resource_id=data_dict[u'resource'][u'id'],
                        record_id=record[u'_id']
                    ),
                    u'copyright': copyright,
                    # Description of image in gallery view
                    u'description': literal(u''.join([u'<span>%s</span>' % t for t in title])),
                    u'title': u' - '.join(title),
                    u'record_id': record[u'_id']
                })
        return images
