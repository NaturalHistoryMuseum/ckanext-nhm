import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.lib.helpers as nhmhelpers

class ThemePlugin(p.SingletonPlugin):
    """
    Theme for the NHM data portal
    """
    p.implements(p.IConfigurer)

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')

class NHMPlugin(p.SingletonPlugin):
    """
    NHM CKAN modifications
        View individual records in a dataset
        Set up NHM (CKAN) model
    """
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)
    p.implements(p.ITemplateHelpers)

    def configure(self, config):
        # TODO: Move adding mat views here?
        pass


    ## IRoutes
    def before_map(self, map):

        # Add view record
        map.connect('record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view')

        # Add dwc view
        map.connect('dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                    controller='ckanext.nhm.controllers.dwc:DarwinCoreController',
                    action='view')

        return map

    def get_actions(self):

        return {
            'record_get':  action.record_get,
            }

    def get_helpers(self):

        helpers = {}

        #  Build a list of helpers from import ckanext.nhm.lib.helpers as nhmhelpers
        for helper in dir(nhmhelpers):

            #  Exclude private
            if not helper.startswith('_'):
                func = getattr(nhmhelpers, helper)

                #  Ensure it's a function
                if hasattr(func, '__call__'):
                    helpers[helper] = func

        return helpers

