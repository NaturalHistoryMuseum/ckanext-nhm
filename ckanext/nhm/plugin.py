import os
import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.schema as nhm_schema
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
        p.toolkit.add_resource('theme/fanstatic', 'nhm_fanstatic')

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
        # facets_dict['creator_user_id'] = 'User'

        return facets_dict
