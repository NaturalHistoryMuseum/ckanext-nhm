import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.schema as nhm_schema

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

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-nhm')

        # Add another public directory for dataset files - this will hopefully be temporary, until DAMS
        p.toolkit.add_public_directory(config, 'files')

    ## IRoutes
    def before_map(self, map):

        # Add controller for KE EMu specimen records
        map.connect('specimen', '/dataset/{package_name}/resource/663c6f9e-aff6-43ee-a5e5-e47bba9928f8/record/{record_id}',
                    controller='ckanext.nhm.controllers.specimen:SpecimenController',
                    action='view', resource_id='663c6f9e-aff6-43ee-a5e5-e47bba9928f8')

        # Add view record
        map.connect('record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view')

        # Add dwc view
        map.connect('dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                    controller='ckanext.nhm.controllers.dwc:DarwinCoreController',
                    action='view')

        # Add static pages
        map.connect('about_data_usage', '/about/data-usage', controller='ckanext.nhm.controllers.page:PageController', action='about_data_usage')
        map.connect('about_credits', '/about/credits', controller='ckanext.nhm.controllers.page:PageController', action='about_credits')

        return map

    # IActions

    def get_actions(self):

        return {
            'record_get':  action.record_get,
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