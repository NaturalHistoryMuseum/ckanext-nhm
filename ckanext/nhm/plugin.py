import ckan.plugins as p
import ckanext.nhm.logic.action as action
import ckanext.nhm.lib.helpers as helpers
import ckanext.nhm.logic.schema as nhm_schema
import logging

DATASET_CATEGORY = 'dataset_category'

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

   # IDatasetForm

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


# class NHMMetadata(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
#     """
#     Add NHM Metadata fields
#     See http://docs.ckan.org/en/latest/extensions/adding-custom-fields.html
#     """
#     p.implements(p.IDatasetForm)
#     p.implements(p.IConfigurer)
#
#     def _modify_package_schema(self, schema):
#
#         # Add category metadata
#         schema.update({
#             'category': [
#                 p.toolkit.get_converter('convert_from_tags')(DATASET_CATEGORY),
#                 p.toolkit.get_validator('ignore_missing')
#             ]
#         })
#
#         # Add custom metadata field
#         schema.update({
#             'temporal_extent': [p.toolkit.get_validator('ignore_missing'), p.toolkit.get_converter('convert_to_extras')]
#         })
#
#         return schema
#
#     def _package_schema_alter_fields(self, schema):
#         """
#         Alter some schema fields, removing the ones we don't want
#         And making required others
#         Also need to add is_required to the form / remove the fields
#
#         List of schema fields: https://github.com/ckan/ckan/blob/3f886918bcd09ae29fda216841f9d318c9ff6c87/ckan/logic/schema.py
#
#         @param schema:
#         @return:
#         """
#         del schema['maintainer']
#         del schema['maintainer_email']
#         del schema['author_email']
#
#         schema['resources']['name'] = [p.toolkit.get_validator('not_empty'), unicode]
#         schema['notes'] = [p.toolkit.get_validator('not_empty'), unicode]
#
#         return schema
#
#     def create_package_schema(self):
#
#         schema = super(NHMMetadata, self).create_package_schema()
#         schema = self._modify_package_schema(schema)
#         schema = self._package_schema_alter_fields(schema)
#         return schema
#
#     def update_package_schema(self):
#
#         schema = super(NHMMetadata, self).update_package_schema()
#         schema = self._modify_package_schema(schema)
#         schema = self._package_schema_alter_fields(schema)
#         return schema
#
#     def show_package_schema(self):
#         schema = super(NHMMetadata, self).show_package_schema()
#         schema = self._package_schema_alter_fields(schema)
#
#         # Don't show vocab tags mixed in with normal 'free' tags
#         # (e.g. on dataset pages, or on the search page)
#         schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))
#
#         # Add category metadata
#         schema.update({
#             'category': [
#                 p.toolkit.get_converter('convert_from_tags')(DATASET_CATEGORY),
#                 p.toolkit.get_validator('ignore_missing')
#             ]
#         })
#
#         # Add custom metadata field
#         schema.update({
#             'temporal_extent': [p.toolkit.get_converter('convert_from_extras'), p.toolkit.get_validator('ignore_missing')]
#         })
#
#         return schema
#
#     def is_fallback(self):
#         # Return True to register this plugin as the default handler for
#         # package types not handled by any other IDatasetForm plugin.
#         return True
#
#     def package_types(self):
#         # This plugin doesn't handle any special package types, it just
#         # registers itself as the default (above).
#         return []
#
#     ## IConfigurer
#     def update_config(self, config):
#         # If going to add a dedicated theme directory for the metadata forms
#         p.toolkit.add_template_directory(config, 'theme/metadata_templates')