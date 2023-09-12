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
from ckan.logic.schema import validator_args
from ckan.plugins import toolkit
from ckan.types import Validator

DATASET_TYPE_VOCABULARY = "dataset_category"

# label: value
UPDATE_FREQUENCIES = {
    "None": "",
    "Daily": "daily",
    "Weekly": "weekly",
    "Monthly": "monthly",
    "Quarterly": "quarterly",
    "Annual": "annual",
    "Discontinued": "discontinued",
    "Never": "never",
}


@validator_args
def record_show_schema(
    not_missing: Validator,
    unicode_safe: Validator,
    resource_id_validator: Validator,
    int_validator: Validator,
    ignore_missing: Validator,
):
    schema = {
        "resource_id": [not_missing, unicode_safe, resource_id_validator],
        "record_id": [not_missing, int_validator],
        "version": [ignore_missing, int_validator],
    }
    return schema


@validator_args
def object_rdf_schema(
    not_missing: Validator,
    unicode_safe: Validator,
    int_validator: Validator,
    ignore_missing: Validator,
):
    schema = {
        "uuid": [not_missing, unicode_safe],
        "format": [not_missing],
        "version": [ignore_missing, int_validator],
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
    convert_from_tags = toolkit.get_converter("convert_to_tags")
    convert_to_extras = toolkit.get_converter("convert_to_extras")
    unicode_safe = toolkit.get_validator("unicode_safe")
    not_empty = toolkit.get_validator("not_empty")
    ignore_missing = toolkit.get_validator("ignore_missing")
    one_of = toolkit.get_validator("one_of")
    boolean_validator = toolkit.get_validator("boolean_validator")

    # Required fields
    schema["title"] = [not_empty, unicode_safe]
    schema["notes"] = [not_empty, unicode_safe]
    schema["author"] = [not_empty, unicode_safe]
    schema["resources"]["name"] = [not_empty, unicode_safe]

    # Add new fields
    schema[DATASET_TYPE_VOCABULARY] = [
        not_empty,
        convert_from_tags(DATASET_TYPE_VOCABULARY),
    ]
    schema["temporal_extent"] = [ignore_missing, unicode_safe, convert_to_extras]
    schema["affiliation"] = [ignore_missing, unicode_safe, convert_to_extras]
    schema["contributors"] = [ignore_missing, unicode_safe, convert_to_extras]
    schema["update_frequency"] = [
        ignore_missing,
        one_of(UPDATE_FREQUENCIES.values()),
        convert_to_extras,
        unicode_safe,
    ]
    schema["promoted"] = [ignore_missing, convert_to_extras, boolean_validator]
    schema["spatial"] = [ignore_missing, convert_to_extras]


@validator_args
def show_package_schema(
    ignore_missing: Validator,
    convert_from_extras: Validator,
    convert_to_tags: Validator,
):
    schema = default_show_package_schema()
    schema["tags"]["__extras"].append(toolkit.get_converter("free_tags_only"))
    schema[DATASET_TYPE_VOCABULARY] = [convert_to_tags(DATASET_TYPE_VOCABULARY)]
    schema["temporal_extent"] = [convert_from_extras, ignore_missing]
    schema["update_frequency"] = [convert_from_extras, ignore_missing]
    schema["affiliation"] = [convert_from_extras, ignore_missing]
    schema["contributors"] = [convert_from_extras, ignore_missing]
    schema["promoted"] = [convert_from_extras, ignore_missing]
    # This is the same as the extras field with key=spatial for ckanext-spatial
    schema["spatial"] = [convert_from_extras, ignore_missing]
    return schema


@validator_args
def get_permanent_url_schema(
    not_missing: Validator,
    ignore_missing: Validator,
    boolean_validator: Validator,
):
    return {
        "field": [not_missing, str],
        "value": [not_missing, str],
        "include_version": [ignore_missing, boolean_validator],
    }
