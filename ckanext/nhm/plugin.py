import pylons
import ckan.plugins as p
import ckan.model as model
from ckan.common import c
import ckanext.nhm.logic.action as action
from ckanext.nhm.model import setup as setup_model
import ckanext.nhm.lib.helpers as nhmhelpers

import ckan.logic as logic
get_action = logic.get_action

class ThemePlugin(p.SingletonPlugin):
    """
    Theme for the NHM data portal
    """
    p.implements(p.IConfigurer)

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'nhm-theme')


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

    ## IConfigurable
    def configure(self, config):
        #  Create tables
        setup_model()

    ## IRoutes
    def before_map(self, map):

        package = model.Package.get(pylons.config['nhm.keemu_dataset_name'])

        if package:
            for pkg_id in [package.id, package.name]:
                # Add default view record controller
                map.connect('record', '/dataset/%s/resource/{resource_id}/record/{record_id}' % pkg_id,
                            controller='ckanext.nhm.controllers.keemu_record:KeEMuRecordController',
                            action='view', id=package.name)

        # TODO: Rename id =>  dataset_id

        # Add default view record controller
        map.connect('record', '/dataset/{id}/resource/{resource_id}/record/{record_id}',
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view')


        # Add map controller
        # TODO: Remove map controller (OKF)
        map.connect('map', '/map/{resource_id}',
                    controller='ckanext.nhm.controllers.map:MapController',
                    action='view')

        return map

    def get_actions(self):

        return {
            'resource_exists':  action.resource_exists, # Wrapper around private _resource_exists
            'record_get':  action.record_get,
            'map_get':  action.map_get,
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

