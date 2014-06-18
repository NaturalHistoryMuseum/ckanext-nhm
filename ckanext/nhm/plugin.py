import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.schema as nhm_schema
from ckan.common import request
from ckanext.spatial.lib import save_package_extent, validate_bbox, bbox_query, bbox_query_ordered
import ckanext.nhm.logic.validators as validators
from ckan.lib.helpers import json

# import is_latitude, is_longitude

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
    p.implements(p.IPackageController, inherit=True)

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-nhm')

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
        return ['dataset']

    def is_fallback(self):
        return True

    def create_package_schema(self):
        return nhm_schema.create_package_schema()

    def update_package_schema(self):
        return nhm_schema.update_package_schema()

    def show_package_schema(self):
        return nhm_schema.show_package_schema()

    def edit(self, package):
        self.check_spatial_extra(package)

    # def check_spatial_extra(self, package):
    #     """
    #     ckanext-spatial required pasting geoJSON into an extra key field, which is nasty
    #     So we allow user to select point / polygon and coordinates
    #     At some point, we'll also a map selection
    #
    #     @param package:
    #     @return:
    #     """
    #
    #     # TODO: Map selection
    #     # TODO: Tidy form
    #
    #     spatial_type = request.params.get('spatial_type', None)
    #
    #     # Delete package extent
    #     if not spatial_type:
    #         save_package_extent(package.id, None)
    #         return
    #
    #     # User has selected a spatial type, so we need to check we have the correct coordinates
    #     if spatial_type == 'point':
    #         spatial_fields = ['point']
    #     elif spatial_type == 'polygon':
    #         spatial_fields = ['east', 'west', 'north', 'south']
    #
    #     error_dict = {}
    #     coordinates = []
    #
    #     for spatial_field in spatial_fields:
    #
    #         coordinate = []
    #
    #         for lat_lon in ['latitude', 'longitude']:
    #             field = '%s_%s' % (spatial_field, lat_lon)
    #             value = request.params.get(field, None)
    #
    #             if not value:
    #                 error_dict[field] = [u'Missing value']
    #             else:
    #
    #                 # Ensure value is a valid latitude / longitude
    #                 validator_func = 'is_%s' % lat_lon
    #
    #                 try:
    #                     # Validate the value
    #                     getattr(validators, validator_func)(value)
    #                 except Invalid:
    #                     # If invalid, add to the error dictionary
    #                     error_dict[field] = [u'Invalid value']
    #
    #             #  Build a list of list coordinates
    #             coordinate.append(float(value))
    #
    #         coordinates.append(coordinate)
    #
    #     if error_dict:
    #         error_summary = {field: errors[0] for field, errors in error_dict.items()}
    #         raise p.toolkit.ValidationError(error_dict, error_summary=error_summary)
    #
    #     else:
    #
    #         # No errors, lets save
    #         geometry = {
    #             'type': 'Point',
    #             'coordinates': coordinates[0]
    #         }
    #
    #         # Save the package extent
    #         save_package_extent(package.id, geometry)
    #
    #         print geometry

