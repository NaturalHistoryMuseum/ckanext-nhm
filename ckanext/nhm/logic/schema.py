#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckanext.nhm.logic.validators import string_max_length, uuid_validator

from ckan.logic.schema import (default_create_package_schema,
                               default_show_package_schema,
                               default_update_package_schema)
from ckan.plugins import toolkit

not_empty = toolkit.get_validator(u'not_empty')
ignore_missing = toolkit.get_validator(u'ignore_missing')
not_missing = toolkit.get_validator(u'not_missing')
resource_id_exists = toolkit.get_validator(u'resource_id_exists')
int_validator = toolkit.get_validator(u'int_validator')
boolean_validator = toolkit.get_validator(u'boolean_validator')
one_of = toolkit.get_validator(u'one_of')

DATASET_TYPE_VOCABULARY = u'dataset_category'

UPDATE_FREQUENCIES = [(u'', u'None'), (u'daily', u'Daily'), (u'weekly', u'Weekly'),
                      (u'monthly', u'Monthly'), (u'quarterly', u'Quarterly'),
                      (u'annual', u'Annual'), (u'discontinued', u'Discontinued'),
                      (u'never', u'Never'), ]


def record_show_schema():
    ''' '''
    schema = {
        u'resource_id': [not_missing, unicode, resource_id_exists],
        u'record_id': [not_missing, int_validator],
        u'version': [ignore_missing, int_validator],
    }
    return schema


def object_rdf_schema():
    ''' '''
    schema = {
        u'uuid': [not_missing, unicode],
        u'format': [not_missing],
        u'version': [ignore_missing, int_validator],
    }
    return schema


def download_original_image_schema():
    ''' '''
    schema = {
        u'resource_id': [not_missing, unicode, resource_id_exists],
        u'record_id': [not_missing, int_validator],
        u'asset_id': [not_missing, uuid_validator],
        u'email': [not_missing, not_empty]
        }
    return schema


def create_package_schema():
    ''' '''
    schema = default_create_package_schema()
    _modify_schema(schema)
    return schema


def update_package_schema():
    ''' '''
    schema = default_update_package_schema()
    _modify_schema(schema)
    return schema


def _modify_schema(schema):
    '''

    :param schema:

    '''
    convert_from_tags = toolkit.get_converter(u'convert_to_tags')
    convert_to_extras = toolkit.get_converter(u'convert_to_extras')
    # Required fields
    schema[u'title'] = [not_empty, string_max_length(255), unicode]
    schema[u'notes'] = [not_empty, string_max_length(4000), unicode]
    schema[u'author'] = [not_empty, unicode]
    schema[u'resources'][u'name'] = [not_empty, string_max_length(255), unicode]
    # Add new fields
    schema[DATASET_TYPE_VOCABULARY] = [not_empty,
                                       convert_from_tags(DATASET_TYPE_VOCABULARY)]
    schema[u'temporal_extent'] = [ignore_missing, unicode, convert_to_extras]
    schema[u'affiliation'] = [ignore_missing, unicode, convert_to_extras]
    schema[u'contributors'] = [ignore_missing, unicode, convert_to_extras]
    schema[u'update_frequency'] = [ignore_missing,
                                   one_of([v[0] for v in UPDATE_FREQUENCIES]),
                                   convert_to_extras, unicode]
    schema[u'promoted'] = [ignore_missing, convert_to_extras, boolean_validator]
    schema[u'spatial'] = [ignore_missing, convert_to_extras]


def show_package_schema():
    ''' '''
    convert_from_extras = toolkit.get_converter(u'convert_from_extras')
    convert_to_tags = toolkit.get_converter(u'convert_from_tags')
    schema = default_show_package_schema()
    schema[u'tags'][u'__extras'].append(toolkit.get_converter(u'free_tags_only'))
    schema[DATASET_TYPE_VOCABULARY] = [convert_to_tags(DATASET_TYPE_VOCABULARY)]
    schema[u'temporal_extent'] = [convert_from_extras, ignore_missing]
    schema[u'update_frequency'] = [convert_from_extras, ignore_missing]
    schema[u'affiliation'] = [convert_from_extras, ignore_missing]
    schema[u'contributors'] = [convert_from_extras, ignore_missing]
    schema[u'promoted'] = [convert_from_extras, ignore_missing]
    # This is the same as the extras field with key=spatial for ckanext-spatial
    schema[u'spatial'] = [convert_from_extras, ignore_missing]
    return schema


def get_permanent_url_schema():
    return {
        u'field': [not_missing, unicode],
        u'value': [not_missing, unicode],
        u'include_version': [ignore_missing, boolean_validator],
    }
