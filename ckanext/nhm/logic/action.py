#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging

from ckan.lib.navl.dictization_functions import validate
from ckan.logic import ActionError
from ckan.plugins import toolkit

import ckanext.nhm.logic.schema as nhm_schema
from ckanext.nhm.dcat.specimen_records import ObjectSerializer
from ckanext.nhm.lib import helpers
from ckanext.nhm.lib.mam import mam_media_request
from ckanext.nhm.lib.record import get_record_by_uuid

log = logging.getLogger(__name__)


def record_show(context, data_dict):
    '''Retrieve an individual record

    :param context:
    :param data_dict:

    '''
    context['user'] = toolkit.c.user or toolkit.c.author
    schema = context.get('schema', nhm_schema.record_show_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    resource_id = toolkit.get_or_bust(data_dict, 'resource_id')
    record_id = toolkit.get_or_bust(data_dict, 'record_id')

    # Retrieve datastore record
    record_data_dict = {
        'resource_id': resource_id,
        'filters': {
            '_id': record_id
        }
    }
    if 'version' in data_dict:
        record_data_dict['version'] = data_dict['version']
    search_result = toolkit.get_action('datastore_search')(context, record_data_dict)

    try:
        record = {
            'data': search_result['records'][0],
            'fields': search_result['fields'],
            'resource_id': resource_id
        }
    except IndexError:
        # If we don't have a result, raise not found
        raise toolkit.ObjectNotFound

    return record


def download_original_image(context, data_dict):
    '''
    Request an original image from the MAM. Before sending request, performs a number of checks
        - The resource exists
        - The record exists on that resource
        - And the image exists on that record

    :param context:
    :param data_dict:
    '''
    # validate the data
    schema = context.get('schema', nhm_schema.download_original_image_schema())
    data_dict, errors = validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    # Get the resource
    resource = toolkit.get_action('resource_show')(context, {'id': data_dict['resource_id']})

    # Retrieve datastore record
    search_result = toolkit.get_action('datastore_search')(context, {
        'resource_id': data_dict['resource_id'],
        'filters': {
            '_id': data_dict['record_id']
        }
    })

    try:
        record = search_result['records'][0]
    except IndexError:
        # If we don't have a result, raise not found
        raise toolkit.ObjectNotFound

    if not _image_exists_on_record(resource, record, data_dict['asset_id']):
        raise toolkit.ObjectNotFound

    try:
        mam_media_request(data_dict['asset_id'], data_dict['email'])
    except Exception as e:
        log.error(e)
        raise ActionError('Could not request original')
    else:
        return 'Original image request successful'


def object_rdf(context, data_dict):
    '''Get record RDF

    :param context:
    :param data_dict:

    '''

    # Validate the data
    context = {
        'user': toolkit.c.user or toolkit.c.author
    }
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
    '''Check the image belongs to the record

    :param resource:
    :param asset_id:
    :param record:

    '''
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
    '''
    Retrieve the permanent URL of a specimen from the specimen collection using the field and value
    to filter the results (i.e. field must equal value for the record to match). A URL is returned
    only if exactly one record is matched by the field and value combination. If more than 1 record
    is matched or if 0 records are matched then an error is returned.

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
    '''
    schema = context.get('schema', nhm_schema.get_permanent_url_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    # extract the request parameters
    field = data_dict['field']
    value = data_dict['value']
    include_version = data_dict.get('include_version', False)

    # create a search dict to use with the datastore_search action
    search_dict = {
        'resource_id': helpers.get_specimen_resource_id(),
        'filters': {
            field: value
        },
        'limit': 1,
    }
    result = toolkit.get_action('datastore_search')(context, search_dict)
    records = result['records']
    total = result['total']
    if total == 0:
        raise toolkit.ValidationError({
            'message': 'No records found matching the given criteria',
            'total': total,
        })
    elif total > 1:
        raise toolkit.ValidationError({
            'message': 'More than 1 record found matching the given criteria',
            'total': total,
        })
    else:
        uuid = records[0]['occurrenceID']
        if include_version:
            # figure out the latest rounded version of the specimen resource data
            version = toolkit.get_action('datastore_get_rounded_version')(context, {
                'resource_id': helpers.get_specimen_resource_id()
            })
            # create a path with the version included
            path = toolkit.url_for('object_view_versioned', uuid=uuid, version=version)
        else:
            path = toolkit.url_for('object_view', uuid=uuid)

        # concatenate the path with the site url and return
        return f'{toolkit.config.get("ckan.site_url")}{path}'
