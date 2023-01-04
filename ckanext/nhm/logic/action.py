#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from importlib.metadata import distributions
from typing import Dict

import ckanext.nhm.logic.schema as nhm_schema
from ckan.plugins import toolkit, plugin_loaded
from ckanext.nhm.dcat.specimen_records import ObjectSerializer
from ckanext.nhm.lib import helpers
from ckanext.nhm.lib.record import get_record_by_uuid
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY

log = logging.getLogger(__name__)


def record_show(context, data_dict):
    """
    Retrieve an individual record.

    :param context:
    :param data_dict:
    """
    context['user'] = toolkit.c.user or toolkit.c.author
    schema = context.get('schema', nhm_schema.record_show_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    resource_id = toolkit.get_or_bust(data_dict, 'resource_id')
    record_id = toolkit.get_or_bust(data_dict, 'record_id')

    # Retrieve datastore record
    record_data_dict = {'resource_id': resource_id, 'filters': {'_id': record_id}}
    if 'version' in data_dict:
        record_data_dict['version'] = data_dict['version']
    search_result = toolkit.get_action('datastore_search')(context, record_data_dict)

    try:
        record = {
            'data': search_result['records'][0],
            'fields': search_result['fields'],
            'resource_id': resource_id,
        }
    except IndexError:
        # If we don't have a result, raise not found
        raise toolkit.ObjectNotFound

    return record


def object_rdf(context, data_dict):
    """
    Get record RDF.

    :param context:
    :param data_dict:
    """

    # Validate the data
    context = {'user': toolkit.c.user or toolkit.c.author}
    schema = context.get('schema', nhm_schema.object_rdf_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    # Raise any validation errors
    if errors:
        raise toolkit.ValidationError(errors)

    # get the record
    version = data_dict.get('version', None)
    record = get_record_by_uuid(data_dict['uuid'], version)
    if record:
        serializer = ObjectSerializer()
        output = serializer.serialize_record(record, data_dict.get('format'), version)
        return output
    raise toolkit.ObjectNotFound


def _image_exists_on_record(resource, record, asset_id):
    """
    Check the image belongs to the record.

    :param resource:
    :param asset_id:
    :param record:
    """
    # FIXME - If no image field use gallery
    image_field = resource.get('_image_field', None)

    # Check the asset ID belongs to the record
    for image in record[image_field]:
        url = image.get('identifier', None)
        if asset_id in url:
            return True
    return False


@toolkit.side_effect_free
def get_permanent_url(context, data_dict):
    """
    Retrieve the permanent URL of a specimen from the specimen collection using the
    field and value to filter the results (i.e. field must equal value for the record to
    match). A URL is returned only if exactly one record is matched by the field and
    value combination. If more than 1 record is matched or if 0 records are matched then
    an error is returned.

    **Params:**

    :param field: the name of the field you would like to filter the records on
    :type field: string
    :param value: the value of the field to filter by
    :type value: string
    :param include_version: whether to include the version in the permanent URL (default: false)
    :type include_version: boolean

    **Results:**

    :returns: the full URL of the specimen
    :rtype: string
    """
    schema = context.get('schema', nhm_schema.get_permanent_url_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    # extract the request parameters
    field = data_dict['field']
    value = data_dict['value']
    include_version = data_dict.get('include_version', False)

    # create a search dict to use with the datastore_search action
    search_dict = {
        'resource_id': helpers.get_specimen_resource_id(),
        'filters': {field: value},
        'limit': 1,
    }
    result = toolkit.get_action('datastore_search')(context, search_dict)
    records = result['records']
    total = result['total']
    if total == 0:
        raise toolkit.ValidationError(
            {
                'message': 'No records found matching the given criteria',
                'total': total,
            }
        )
    elif total > 1:
        raise toolkit.ValidationError(
            {
                'message': 'More than 1 record found matching the given criteria',
                'total': total,
            }
        )
    else:
        uuid = records[0]['occurrenceID']
        if include_version:
            # figure out the latest rounded version of the specimen resource data
            version = toolkit.get_action('datastore_get_rounded_version')(
                context, {'resource_id': helpers.get_specimen_resource_id()}
            )
            # create a path with the version included
            path = toolkit.url_for('object_view_versioned', uuid=uuid, version=version)
        else:
            path = toolkit.url_for('object_view', uuid=uuid)

        # concatenate the path with the site url and return
        return f'{toolkit.config.get("ckan.site_url")}{path}'


@toolkit.chained_action
def user_show(next_action, context, data_dict):
    # FIXME: temporary override until we update to ckan 2.10
    current_user = context.get('auth_user_obj')
    if (
        'id' not in data_dict
        and 'user_obj' not in data_dict
        and current_user is not None
    ):
        data_dict['id'] = context['auth_user_obj'].id
    return next_action(context, data_dict)


@toolkit.chained_action
def package_update(next_action, context, pkg_dict):
    # force lowercase for tags with no vocabulary
    category_tags = [
        t['name']
        for t in toolkit.get_action('vocabulary_show')(
            {}, {'id': DATASET_TYPE_VOCABULARY}
        )['tags']
    ]
    tags = []
    for tag in pkg_dict.get('tags', []):
        if tag.get('vocabulary_id'):
            tags.append(tag)
            continue
        if tag['name'] in category_tags:
            # this is a reserved tag, don't use it
            continue
        tag['name'] = tag['name'].lower()
        if tag['name'] not in [t['name'] for t in tags]:
            tags.append(tag)
    pkg_dict['tag_string'] = ','.join(
        [t['name'] for t in tags if not t.get('vocabulary_id')]
    )
    pkg_dict['tags'] = tags

    return next_action(context, pkg_dict)


@toolkit.chained_action
def resource_create(next_action, context, res_dict):
    # force uppercase and trim '.' for file formats
    res_dict['format'] = res_dict.get('format', '').upper().strip('.')
    return next_action(context, res_dict)


@toolkit.chained_action
def resource_update(next_action, context, res_dict):
    # force uppercase and trim '.' for file formats
    res_dict['format'] = res_dict.get('format', '').upper().strip('.')
    return next_action(context, res_dict)


@toolkit.side_effect_free
def show_extension_versions(context, data_dict) -> Dict[str, str]:
    """
    Find all the installed extension packages and return their names and versions.

    :return: a dict of extension package name -> version
    """
    dists = []

    for distribution in distributions():
        # ckan will show up in this list and will pass the lower tests, ignore it
        if distribution.name == 'ckan':
            continue
        # loop through the entry points in the package and if they have a ckan plugin
        # entry, and it's loaded, add it to the extensions dict
        for entry_point in distribution.entry_points:
            if entry_point.group == 'ckan.plugins' and plugin_loaded(entry_point.name):
                dists.append(distribution)
                # break on the first matching entry point as that's enough to confirm
                # that the package as a whole should be in the list
                break

    # sort the result alphabetically
    return {dist.name: dist.version for dist in sorted(dists, key=lambda d: d.name)}
