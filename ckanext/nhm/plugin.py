# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from collections import OrderedDict

import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.action as nhm_action
import ckanext.nhm.logic.schema as nhm_schema
import os
import re
import requests
from beaker.cache import cache_managers
from ckanext.ckanpackager.interfaces import ICkanPackager
from ckanext.contact.interfaces import IContact
from ckanext.doi.interfaces import IDoi
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.nhm import routes
from ckanext.nhm.lib.cache import cache_clear_nginx_proxy
from ckanext.nhm.lib.eml import generate_eml
from ckanext.nhm.lib.helpers import (get_site_statistics,
                                     resource_view_get_filter_options)  # NOTE: Need
# to import a function with a cached decorator so clear caches works
from ckanext.nhm.settings import COLLECTION_CONTACTS
from ckanext.versioned_datastore.interfaces import IVersionedDatastore
from pylons import config
from webhelpers.html import literal

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as p
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

# NOTE: Need to import a function with a cached decorator so clear caches works.
# assigning here as the function is not used anywhere and would be lost in automatic
# import optimisations
_this_function_has_a_cached_decorator = get_site_statistics

log = logging.getLogger(__name__)

MAX_LIMIT = 5000


class NHMPlugin(SingletonPlugin, toolkit.DefaultDatasetForm):
    '''NHM CKAN modifications. View individual records in a dataset, Set up NHM
    (CKAN) model

    '''

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(root_dir, u'ckanext', u'nhm', u'theme', u'templates')

    implements(interfaces.IBlueprint, inherit=True)
    implements(interfaces.IRoutes, inherit=True)
    implements(interfaces.IActions, inherit=True)
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IConfigurer, inherit=True)
    implements(interfaces.IDatasetForm, inherit=True)
    implements(interfaces.IFacets, inherit=True)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.IResourceController, inherit=True)
    implements(IContact)
    implements(IDoi)
    implements(IGalleryImage)
    implements(ICkanPackager)
    implements(IVersionedDatastore)

    ## IConfigurer
    def update_config(self, config):
        '''
        ..seealso:: ckan.plugins.interfaces.IConfigurer.update_config
        :param config:
        '''
        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates

        config[u'extra_template_paths'] = u','.join(
            [self.template_dir, config.get(u'extra_template_paths', u'')])

        toolkit.add_public_directory(config, u'theme/public')
        toolkit.add_resource(u'theme/fanstatic', u'ckanext-nhm')

        # Add another public directory for dataset files - this will hopefully
        # be temporary, until DAMS
        toolkit.add_public_directory(config, u'files')

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints

    ## IRoutes
    def before_map(self, _map):
        '''
        ..seealso:: ckan.plugins.interfaces.IRoutes.before_map
        :param _map:
        '''

        # Add view record
        _map.connect('record_versioned',
                     '/dataset/{package_name}/resource/{resource_id}/record/{'
                     'record_id}/{version}',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='view', requirements={
                'version': '\d+'
                })
        _map.connect('record',
                     '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='view')

        # Add dwc view
        _map.connect('dwc_versioned',
                     '/dataset/{package_name}/resource/{resource_id}/record/{'
                     'record_id}/dwc/{version}',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='dwc', requirements={
                'version': '\d+'
                })
        _map.connect('dwc',
                     '/dataset/{package_name}/resource/{resource_id}/record/{'
                     'record_id}/dwc',
                     controller='ckanext.nhm.controllers.record:RecordController',
                     action='dwc')

        # About pages
        _map.connect('about_citation', '/about/citation',
                     controller='ckanext.nhm.controllers.about:AboutController',
                     action='citation')
        _map.connect('about_download', '/about/download',
                     controller='ckanext.nhm.controllers.about:AboutController',
                     action='download')
        _map.connect('about_licensing', '/about/licensing',
                     controller='ckanext.nhm.controllers.about:AboutController',
                     action='licensing')
        _map.connect('about_credits', '/about/credits',
                     controller='ckanext.nhm.controllers.about:AboutController',
                     action='credits')

        # Legal pages
        _map.connect('legal_privacy', '/privacy',
                     controller='ckanext.nhm.controllers.legal:LegalController',
                     action='privacy')
        _map.connect('legal_terms', '/terms-conditions',
                     controller='ckanext.nhm.controllers.legal:LegalController',
                     action='terms')

        # About stats pages
        _map.connect('stats_resources', '/about/statistics/resources',
                     controller='ckanext.nhm.controllers.stats:StatsController',
                     action='resources', ckan_icon='bar-chart')
        _map.connect('stats_contributors', '/about/statistics/contributors',
                     controller='ckanext.nhm.controllers.stats:StatsController',
                     action='contributors', ckan_icon='user')
        _map.connect('stats_records', '/about/statistics/records',
                     controller='ckanext.nhm.controllers.stats:StatsController',
                     action='records', ckan_icon='file-text')

        # Dataset metrics
        _map.connect('dataset_metrics', '/dataset/metrics/{id}',
                     controller='ckanext.nhm.controllers.stats:StatsController',
                     action='dataset_metrics', ckan_icon='bar-chart')
        # NOTE: Access to /datastore/dump/{resource_id} is prevented by NGINX

        object_controller = 'ckanext.nhm.controllers.object:ObjectController'

        _map.connect('object_rdf_versioned', '/object/{uuid}/{version}.{_format}',
                     controller=object_controller, action='rdf',
                     requirements={
                         '_format': 'xml|rdf|n3|ttl|jsonld',
                         'version': '\d+'
                         })

        _map.connect('object_rdf', '/object/{uuid}.{_format}',
                     controller=object_controller, action='rdf',
                     requirements={
                         '_format': 'xml|rdf|n3|ttl|jsonld'
                         })

        # Permalink for specimens - needs to come after the DCAT format dependent
        _map.connect('object_view_versioned', '/object/{uuid}/{version}',
                     controller=object_controller,
                     action='view', requirements={
                'version': '\d+'
                })
        _map.connect('object_view', '/object/{uuid}',
                     controller=object_controller,
                     action='view')

        # Redirect the old specimen url to the object
        _map.redirect(u'/specimen/{url:.*}', u'/object/{url}')

        # The DCAT plugin breaks these links if enable content negotiation is enabled
        # because it maps to /dataset/{_id} without excluding these actions
        # So we re=add them here to make sure it's working
        # TODO: are these still broken?
        # _map.connect(u'add dataset', u'/dataset/new', controller=u'dataset',
        #              action=u'new')
        _map.connect(u'/dataset/{action}',
                     controller=u'dataset',
                     requirements=dict(action=u'|'.join([
                         u'list',
                         u'autocomplete'
                         ])))

        return _map

    # IActions
    def get_actions(self):
        '''
        ..seealso:: ckan.plugins.interfaces.IActions.get_actions
        '''
        return {
            u'record_show': nhm_action.record_show,
            u'object_rdf': nhm_action.object_rdf,
            u'download_image': nhm_action.download_original_image
            }

    # ITemplateHelpers
    def get_helpers(self):
        '''
        ..seealso:: ckan.plugins.interfaces.ITemplateHelpers.get_helpers
        '''

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
        del facets_dict[u'organization']
        del facets_dict[u'groups']

        # Add author facet as the first item
        facets_dict = OrderedDict([(u'author', u'Authors')] + facets_dict.items())
        facets_dict[u'creator_user_id'] = u'Users'

        return facets_dict

    ## IPackageController
    def before_search(self, data_dict):
        '''
        ..seealso:: ckan.plugins.interfaces.IPackageController.before_search
        '''
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get(u'sort', None):
            data_dict[u'sort'] = u'promoted asc, metadata_modified desc'

        return data_dict

    def before_view(self, pkg_dict):
        '''
        ..seealso:: ckan.plugins.interfaces.IPackageController.before_view

        :returns: pkg_dict with full list of authors renamed to all_authors, and author
                  field truncated (with HTML!) if necessary

        '''
        pkg_dict[u'all_authors'] = pkg_dict[u'author']
        pkg_dict[u'author'] = helpers.dataset_author_truncate(pkg_dict[u'author'])
        return pkg_dict

    ## IContact
    def mail_alter(self, mail_dict, data_dict):
        '''
        ..seealso:: ckanext.contact.interfaces.IContact.mail_alter
        '''

        # Get the submitted data values
        package_id = data_dict.get(u'package_id', None)
        package_name = data_dict.get(u'package_name', None)
        resource_id = data_dict.get(u'resource_id', None)
        record_id = data_dict.get(u'record_id', None)

        context = {
            u'user': toolkit.c.user or toolkit.c.author
            }

        # URL to provide as link to contact email body
        # Over written by linking to record / resource etc., - see below
        url = None

        # Has the user selected a department
        department = data_dict.get(u'department', None)

        # Build dictionary of URLs
        urls = {}
        if package_id:
            urls[u'dataset'] = toolkit.url_for(u'dataset.read',
                                               id=package_id, qualified=True)
            if resource_id:
                urls[u'resource'] = toolkit.url_for(u'resource.read',
                                                    id=package_id,
                                                    resource_id=resource_id,
                                                    qualified=True)
                if record_id:
                    urls[u'record'] = toolkit.url_for(u'record.view',
                                                      package_name=package_id,
                                                      resource_id=resource_id,
                                                      record_id=record_id,
                                                      qualified=True)

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
                    u'body'] += u'\nThe contactee has chosen to send this to the {0} ' \
                                u'department. Our apologies if this enquiry isn\'t ' \
                                u'relevant - please forward this onto data@nhm.ac.uk ' \
                                u'and we will respond.\nMany thanks, Data Portal ' \
                                u'team\n\n'.format(department)
                # If we have a package ID, load the package
        elif package_id:
            package_dict = toolkit.get_action(u'package_show')(context, {
                u'id': package_id
                })
            # Load the user - using model rather user_show API which loads all the
            # users packages etc.,
            user_obj = model.User.get(package_dict[u'creator_user_id'])
            mail_dict[u'recipient_name'] = user_obj.fullname or user_obj.name
            # Update send to with creator username
            mail_dict[u'recipient_email'] = user_obj.email
            mail_dict[u'subject'] = u'Message regarding dataset: %s' % package_dict[
                u'title']
            mail_dict[
                u'body'] += u'\n\nYou have been sent this enquiry via the data portal ' \
                            u'as you are the author of dataset %s.  Our apologies if ' \
                            u'this isn\'t relevant - please forward this onto ' \
                            u'data@nhm.ac.uk and we will respond.\nMany thanks, ' \
                            u'Data Portal team\n\n' % \
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
        ..seealso:: ckan.plugins.interfaces.IPackageController.after_update
        :param context:
        :param pkg_dict:

        '''
        for resource in pkg_dict.get(u'resources', []):
            # If this is the specimen resource ID, clear the collection stats
            if u'id' in resource:
                if resource[u'id'] in [helpers.get_specimen_resource_id(),
                                       helpers.get_indexlot_resource_id()]:
                    log.info(u'Clearing caches')
                    # Quick and dirty, delete all caches when indexlot or specimens
                    # are updated
                    for _cache in cache_managers.values():
                        _cache.clear()

        # Clear the NGINX proxy cache
        cache_clear_nginx_proxy()

    ## IDoi
    def build_metadata(self, pkg_dict, metadata_dict):
        '''
        ..seealso:: ckanext.doi.interfaces.IDoi.build_metadata
        '''
        metadata_dict[u'resource_type'] = pkg_dict.get(u'dataset_category', None)
        if isinstance(metadata_dict[u'resource_type'], list) and metadata_dict[
            u'resource_type']:
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
        ..seealso:: ckanext.doi.interfaces.IDoi.metadata_to_xml
        '''
        if u'contributors' in metadata:
            xml_dict[u'resource'][u'contributors'] = {
                u'contributor': [],
                }
            for contributor in metadata[u'contributors']:
                contributor[u'@contributorType'] = u'Researcher'
                xml_dict[u'resource'][u'contributors'][u'contributor'].append(
                    contributor)

        # FIXME - Datacite 3.1 isn't accepting affiliation in the creator field
        # if 'affiliation' in metadata:
        #     xml_dict['resource']['creators']['creator'][0]['affiliation'] = metadata[
        #         'affiliation']
        return xml_dict

    # IGalleryImage
    def image_info(self):
        '''Return info for this plugin. If resource type is set, only dataset of that
        type will be available.

        ..seealso:: ckanext.gallery.plugins.interfaces.IGalleryImage.image_info

        '''
        return {
            'title': 'DwC associated media',
            'resource_type': ['dwc', 'csv', 'tsv'],
            'field_type': ['json']
            }

    ## IGalleryImage
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
    def before_package_request(self, resource_id, package_id, packager_url,
                               request_params):
        '''
        Modify the request params that are about to be sent through to the
        ckanpackager backend so that an EML param is
        included.

        :param resource_id: the resource id of the resource that is about to be packaged
        :param package_id: the package id of the resource that is about to be packaged
        :param packager_url: the target url for this packaging request
        :param request_params: a dict of parameters that will be sent with the request
        :return: the url and the params as a tuple
        '''
        resource = toolkit.get_action(u'resource_show')(None, {
            u'id': resource_id
            })
        package = toolkit.get_action(u'package_show')(None, {
            u'id': package_id
            })
        if resource.get(u'datastore_active', False) and resource.get(u'format',
                                                                     u'').lower() == \
                u'dwc':
            # if it's a datastore resource and it's in the DwC format, add EML
            request_params[u'eml'] = generate_eml(package, resource)
        return packager_url, request_params

    # IVersionedDatastore
    def datastore_modify_data_dict(self, context, data_dict):
        '''
        This function allows overriding of the data dict before datastore_search gets
        to it. We use
        this opportunity to:

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
        '''
        # remove our custom filters from the filters dict, we'll add them ourselves in
        # the modify
        # search function below
        if u'filters' in data_dict:
            # figure out which options are available for this resource
            resource_show = p.toolkit.get_action(u'resource_show')
            resource = resource_show(context, {
                u'id': data_dict[u'resource_id']
                })
            options = resource_view_get_filter_options(resource)
            # we'll store the filters that need applying on the context to avoid
            # repeating our work
            # in the modify search function below
            context[u'option_filters'] = []
            for option in options:
                if option.name in data_dict[u'filters']:
                    # if the option is in the filters, delete it and add it's filter
                    # to the context
                    del data_dict[u'filters'][option.name]
                    context[u'option_filters'].append(option.filter_dsl)

        if u'sort' not in data_dict:
            # by default sort the EMu resources by modified so that the latest records
            # are first
            if data_dict['resource_id'] in {helpers.get_specimen_resource_id(),
                                            helpers.get_artefact_resource_id(),
                                            helpers.get_indexlot_resource_id()}:
                data_dict['sort'] = ['modified desc']

        return data_dict

    # IVersionedDatastore
    def datastore_modify_search(self, context, original_data_dict, data_dict, search):
        '''
        This function allows us to modify the search object itself before it is
        serialised and sent
        to elasticsearch. In this function we currently only do one thing: add the actual
        elasticsearch query DSL for each filter option that was removed in the
        datastore_modify_data_dict above (they are stored in the context so that we
        can identify
        which ones to add in).

        :param context: the context dict
        :param original_data_dict: the original data dict before any plugins modified it
        :param data_dict: the data dict after all plugins have had a chance to modify it
        :param search: the search object itself
        :return: the modified search object
        '''
        # add our custom filters by looping through the filter dsl objects on the
        # context. These are
        # added by the datastore_modify_data_dict function above if any of our custom
        # filters exist
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
        This function allows us to modify the field definitions before they are
        returned as part of
        the datastore_search action. All we do here is just modify the associatedMedia
        field if it
        exists to ensure it is treated as an array.

        :param resource_id: the resource id
        :param mapping: the original mapping dict returned by elasticsearch from which
        the field
                        info has been derived
        :param fields: the fields dict itself
        :return: the fields dict
        '''
        # if we're dealing with one of our EMu backed resources and the
        # associatedMedia field is
        # present set its type to array rather than string (the default). This isn't
        # really
        # necessary from recline's point of view as we override the render of this
        # field's data
        # anyway, but for completeness and correctness we'll do the override
        if resource_id in {helpers.get_specimen_resource_id(),
                           helpers.get_artefact_resource_id(),
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

    # IVersionedDatastore
    def datastore_after_indexing(self, request, eevee_stats, stats_id):
        try:
            # whenever anything is indexed, we should clear the cache, catch exceptions on failures
            # and only wait a couple of seconds for the request to complete
            requests.request(u'purge', config.get(u'ckan.site_url'), timeout=2)
        except:
            pass
