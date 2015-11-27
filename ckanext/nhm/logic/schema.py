import ckan.plugins as p

from ckan.logic.schema import (
    default_create_package_schema,
    default_update_package_schema,
    default_show_package_schema
    )

from ckanext.nhm.logic.validators import string_max_length, uuid_validator
from formencode.validators import OneOf

get_converter = p.toolkit.get_converter
get_validator = p.toolkit.get_validator

# Core validators and converters
not_empty = get_validator('not_empty')
ignore_missing = get_validator('ignore_missing')
not_missing = get_validator('not_missing')
resource_id_exists = get_validator('resource_id_exists')
int_validator = get_validator('int_validator')
boolean_validator = get_validator('boolean_validator')

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
        'resource_id': [not_missing, unicode, resource_id_exists],
        'record_id': [not_missing, int_validator]
    }
    return schema


def download_original_image_schema():
    schema = {
        'resource_id': [not_missing, unicode, resource_id_exists],
        'record_id': [not_missing, int_validator],
        'asset_id': [not_missing, uuid_validator],
        'email': [not_missing, not_empty]
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
    convert_from_tags = get_converter('convert_to_tags')
    convert_to_extras = get_converter('convert_to_extras')
    # Required fields
    schema['title'] = [not_empty, string_max_length(255), unicode]
    schema['notes'] = [not_empty, string_max_length(4000), unicode]
    schema['author'] = [not_empty, unicode]
    schema['resources']['name'] = [not_empty, string_max_length(255), unicode]
    # Add new fields
    schema[DATASET_TYPE_VOCABULARY] = [not_empty, convert_from_tags(DATASET_TYPE_VOCABULARY)]
    schema['temporal_extent'] = [ignore_missing, unicode, convert_to_extras]
    schema['affiliation'] = [ignore_missing, unicode, convert_to_extras]
    schema['contributors'] = [ignore_missing, unicode, convert_to_extras]
    schema['update_frequency'] = [ignore_missing, OneOf([v[0] for v in UPDATE_FREQUENCIES]), convert_to_extras, unicode]
    schema['promoted'] = [ignore_missing, convert_to_extras, boolean_validator]
    schema['spatial'] = [ignore_missing, convert_to_extras]


def show_package_schema():
    convert_from_extras = get_converter('convert_from_extras')
    convert_to_tags = get_converter('convert_from_tags')
    schema = default_show_package_schema()
    schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))
    schema[DATASET_TYPE_VOCABULARY] = [convert_to_tags(DATASET_TYPE_VOCABULARY)]
    schema['temporal_extent'] = [convert_from_extras, ignore_missing]
    schema['update_frequency'] = [convert_from_extras, ignore_missing]
    schema['affiliation'] = [convert_from_extras, ignore_missing]
    schema['contributors'] = [convert_from_extras, ignore_missing]
    schema['promoted'] = [convert_from_extras, ignore_missing]
    # This is the same as the extras field with key=spatial for ckanext-spatial
    schema['spatial'] = [convert_from_extras, ignore_missing]
    return schema