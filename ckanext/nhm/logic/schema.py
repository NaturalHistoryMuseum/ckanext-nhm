#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.logic.schema import (
    default_create_package_schema,
    default_show_package_schema,
    default_update_package_schema,
)
from ckan.plugins import toolkit

from ckanext.nhm.logic.validators import string_max_length, uuid_validator

not_empty = toolkit.get_validator('not_empty')
ignore_missing = toolkit.get_validator('ignore_missing')
not_missing = toolkit.get_validator('not_missing')
resource_id_exists = toolkit.get_validator('resource_id_exists')
int_validator = toolkit.get_validator('int_validator')
boolean_validator = toolkit.get_validator('boolean_validator')
one_of = toolkit.get_validator('one_of')

DATASET_TYPE_VOCABULARY = 'dataset_category'

UPDATE_FREQUENCIES = [
    ('', 'None'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annual', 'Annual'),
    ('discontinued', 'Discontinued'),
    ('never', 'Never'),
]


def record_show_schema():
    schema = {
        'resource_id': [not_missing, str, resource_id_exists],
        'record_id': [not_missing, int_validator],
        'version': [ignore_missing, int_validator],
    }
    return schema


def object_rdf_schema():
    schema = {
        'uuid': [not_missing, str],
        'format': [not_missing],
        'version': [ignore_missing, int_validator],
    }
    return schema


def create_package_schema():
    schema = default_create_package_schema()
    _modify_schema(schema)
    return schema


def update_package_schema():
    schema = default_update_package_schema()
    _modify_schema(schema)
    return schema


def _modify_schema(schema):
    convert_from_tags = toolkit.get_converter('convert_to_tags')
    convert_to_extras = toolkit.get_converter('convert_to_extras')
    # Required fields
    schema['title'] = [not_empty, string_max_length(255), str]
    schema['notes'] = [not_empty, string_max_length(4000), str]
    schema['author'] = [not_empty, str]
    schema['resources']['name'] = [not_empty, string_max_length(255), str]
    # Add new fields
    schema[DATASET_TYPE_VOCABULARY] = [
        not_empty,
        convert_from_tags(DATASET_TYPE_VOCABULARY),
    ]
    schema['temporal_extent'] = [ignore_missing, str, convert_to_extras]
    schema['affiliation'] = [ignore_missing, str, convert_to_extras]
    schema['contributors'] = [ignore_missing, str, convert_to_extras]
    schema['update_frequency'] = [
        ignore_missing,
        one_of([v[0] for v in UPDATE_FREQUENCIES]),
        convert_to_extras,
        str,
    ]
    schema['promoted'] = [ignore_missing, convert_to_extras, boolean_validator]
    schema['spatial'] = [ignore_missing, convert_to_extras]


def show_package_schema():
    convert_from_extras = toolkit.get_converter('convert_from_extras')
    convert_to_tags = toolkit.get_converter('convert_from_tags')
    schema = default_show_package_schema()
    schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
    schema[DATASET_TYPE_VOCABULARY] = [convert_to_tags(DATASET_TYPE_VOCABULARY)]
    schema['temporal_extent'] = [convert_from_extras, ignore_missing]
    schema['update_frequency'] = [convert_from_extras, ignore_missing]
    schema['affiliation'] = [convert_from_extras, ignore_missing]
    schema['contributors'] = [convert_from_extras, ignore_missing]
    schema['promoted'] = [convert_from_extras, ignore_missing]
    # This is the same as the extras field with key=spatial for ckanext-spatial
    schema['spatial'] = [convert_from_extras, ignore_missing]
    return schema


def get_permanent_url_schema():
    return {
        'field': [not_missing, str],
        'value': [not_missing, str],
        'include_version': [ignore_missing, boolean_validator],
    }
