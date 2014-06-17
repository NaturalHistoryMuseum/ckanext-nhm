import ckan.plugins as p

from ckan.logic.schema import (
    default_create_package_schema,
    default_update_package_schema,
    default_show_package_schema
    )

from ckanext.nhm.logic.validators import string_max_length

get_converter = p.toolkit.get_converter
get_validator = p.toolkit.get_validator

# Core validators and converters
not_empty = get_validator('not_empty')
ignore_missing = get_validator('ignore_missing')
not_missing = get_validator('not_missing')
resource_id_exists = get_validator('resource_id_exists')
int_validator = get_validator('int_validator')

DATASET_CATEGORY = 'dataset_category'


def record_get_schema():

    schema = {
        'resource_id': [not_missing, unicode, resource_id_exists],
        'record_id': [not_missing, int_validator]
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
    schema['resources']['name'] = [not_empty, string_max_length(255), unicode]

    schema['category'] = [convert_from_tags(DATASET_CATEGORY), ignore_missing]
    schema['temporal_extent'] = [ignore_missing, convert_to_extras]
    schema['update_frequency'] = [ignore_missing, convert_to_extras]

def show_package_schema():

    convert_from_extras = get_converter('convert_from_extras')
    convert_to_tags = get_converter('convert_from_tags')

    schema = default_show_package_schema()
    schema['tags']['__extras'].append(p.toolkit.get_converter('free_tags_only'))
    schema['category'] = [convert_to_tags(DATASET_CATEGORY)]
    schema['temporal_extent'] = [convert_from_extras]
    schema['update_frequency'] = [convert_from_extras]
    return schema