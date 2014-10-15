import os
import re
import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.logic.schema as nhm_schema
from ckanext.cacheapi.interfaces import ICache
from ckanext.datastore.interfaces import IDatastore
from collections import OrderedDict
from pylons import config

Invalid = p.toolkit.Invalid

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
    p.implements(ICache, inherit=True)
    p.implements(IDatastore)

    ## IConfigurer
    def update_config(self, config):

        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(root_dir, 'ckanext', 'nhm', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])

        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-nhm')
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-nhm-fanstatic')

        # Add another public directory for dataset files - this will hopefully be temporary, until DAMS
        p.toolkit.add_public_directory(config, 'files')

    ## IRoutes
    def before_map(self, map):

        resource_id = config.get("ckanext.nhm.collection_resource_id")

        # Add controller for KE EMu specimen records
        map.connect('specimen', '/dataset/{package_name}/resource/%s/record/{record_id}' % resource_id,
                    controller='ckanext.nhm.controllers.specimen:SpecimenController',
                    action='view', resource_id=resource_id)

        # Add view record
        map.connect('record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view')

        # Add dwc view
        map.connect('dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                    controller='ckanext.nhm.controllers.dwc:DarwinCoreController',
                    action='view')

        # About pages
        map.connect('about_citation', '/about/citation', controller='ckanext.nhm.controllers.about:AboutController', action='citation')
        map.connect('about_download', '/about/download', controller='ckanext.nhm.controllers.about:AboutController', action='download')
        map.connect('about_licensing', '/about/licensing', controller='ckanext.nhm.controllers.about:AboutController', action='licensing')
        map.connect('about_credits', '/about/credits', controller='ckanext.nhm.controllers.about:AboutController', action='credits')

        # Legal pages
        map.connect('legal_privacy', '/privacy', controller='ckanext.nhm.controllers.legal:LegalController', action='privacy')
        map.connect('legal_terms', '/terms-conditions', controller='ckanext.nhm.controllers.legal:LegalController', action='terms')

        # About stats pages
        map.connect('stats_datasets', '/about/statistics/datasets', controller='ckanext.nhm.controllers.stats:StatsController', action='datasets', ckan_icon='bar-chart')
        map.connect('stats_contributors', '/about/statistics/contributors', controller='ckanext.nhm.controllers.stats:StatsController', action='contributors', ckan_icon='user')
        map.connect('stats_records', '/about/statistics/records', controller='ckanext.nhm.controllers.stats:StatsController', action='records', ckan_icon='file-text')

        # Dataset metrics
        map.connect('dataset_metrics', '/dataset/metrics/{id}', controller='ckanext.nhm.controllers.stats:StatsController', action='dataset_metrics', ckan_icon='bar-chart')

        return map

    # IActions
    def get_actions(self):

        return {
            'record_get':  action.record_get
        }

    # ITemplateHelpers
    def get_helpers(self):
        import ckanext.nhm.lib.helpers as helpers

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

   # IDatasetForm - CKAN Metadata
   # See See http://docs.ckan.org/en/latest/extensions/adding-custom-fields.html

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

    # IFacets
    def dataset_facets(self, facets_dict, package_type):

        # Remove organisations and groups
        del facets_dict['organization']
        del facets_dict['groups']

        # Add author facet as the first item
        facets_dict = OrderedDict([('author', 'Authors')] + facets_dict.items())
        facets_dict['creator_user_id'] = 'User'

        return facets_dict

    # IPackageController
    def before_search(self, data_dict):
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get('sort', None):
            data_dict['sort'] = u'promoted asc, metadata_modified desc'

        return data_dict

    # ICache
    def get_caches(self, context, cache_dict):

        # Stats pages to clear by group
        cache_dict['stats'] = [
            '/',
            'about'
        ]

        return cache_dict

    ## IDataStore
    def datastore_validate(self, context, data_dict, all_field_ids):
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_filter_options(resource)
            for o in options:
                if o in data_dict['filters']:
                    del data_dict['filters'][o]
        return data_dict

    def datastore_search(self, context, data_dict, all_field_ids, query_dict):
        # Add our options filters
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_filter_options(resource)
            for o in options:
                if o in data_dict['filters'] and 'true' in data_dict['filters'][o]:
                    if 'sql' in options[o]:
                        query_dict['where'].append(options[o]['sql'])
                elif 'sql_false' in options[o]:
                    query_dict['where'].append(options[o]['sql_false'])

        # Enhance the full text search, by adding support for double quoted expressions. We leave the
        # full text search query intact (so we benefit from the full text index) and add an additonal
        # LIKE statement for each quoted group.
        if 'q' in data_dict and not isinstance(data_dict['q'], dict):
            for match in re.findall('"[^"]+"', data_dict['q']):
                query_dict['where'].append((
                    '"{}"::text LIKE %s'.format(resource['id']),
                    '%' + match[1:-1] + '%'
                ))

        # CKAN's field auto-completion uses full text search on individual fields. This causes
        # problems because of stemming issues, and is quite slow on our data set (even with an
        # appropriate index). We detect this type of queries and replace them with a LIKE query.
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
                    'ts_query': ''
                }
        return query_dict

    def datastore_delete(self, context, data_dict, all_field_ids, query_dict):
        return query_dict

def resource_filter_options(resource):
    """Return the list of filter options for the given resource.

    Note that this is the master source for the list of available options.

    We may want to have this dependent on available fields (rather than
    resource format), so it's useful to keep this as a function (rather
    than a static dict).

    @type resource: dict
    @param resource: Dictionary representing a resource
    @rtype: dict
    @return: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - sql: Optional. The SQL WHERE statement to use when this
                       option is checked (as a tuple containing statement
                       and value replacements);
                - sql_false: Optional. The SQL WHERE statement to use when
                             this option is unchecked (as a tuple containing
                             statement and value replacements).
    """
    table = resource['id']
    # Get the resource-dependent filter option list
    if resource['format'].lower() == 'dwc':
        return {
            '_has_type': {
                'label': 'Has type',
                'sql': ('"{}"."typeStatus" IS NOT NULL'.format(table),)
            },
            '_has_image': {
                'label': 'Has image',
                'sql': ('"{}"."associatedMedia" IS NOT NULL'.format(table),)
            },
            '_has_lat_long': {
                'label': 'Has lat/long',
                'sql': ('"{}"."_geom" IS NOT NULL'.format(table),)
            }
        }
    else:
        return {}
