#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging

import ckanext.nhm.logic.schema as nhm_schema
from ckanext.nhm.lib.mam import mam_media_request
from ckanext.nhm.dcat.specimen_records import ObjectSerializer
from ckanext.nhm.lib.record import get_record_by_uuid
from ckanext.nhm.lib import helpers

from ckan.logic import ActionError
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def record_show(context, data_dict):
    '''Retrieve an individual record

    :param context:
    :param data_dict:

    '''
    context[u'user'] = toolkit.c.user or toolkit.c.author
    schema = context.get(u'schema', nhm_schema.record_show_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    resource_id = toolkit.get_or_bust(data_dict, u'resource_id')
    record_id = toolkit.get_or_bust(data_dict, u'record_id')

    # Retrieve datastore record
    record_data_dict = {
        u'resource_id': resource_id,
        u'filters': {
            u'_id': record_id
            }
        }
    if u'version' in data_dict:
        record_data_dict[u'version'] = data_dict[u'version']
    search_result = toolkit.get_action(u'datastore_search')(context, record_data_dict)

    try:
        record = {
            u'data': search_result[u'records'][0],
            u'fields': search_result[u'fields'],
            u'resource_id': resource_id
            }
    except IndexError:
        # If we don't have a result, raise not found
        raise toolkit.ObjectNotFound

    return record


def download_original_image(context, data_dict):
    '''Request an original image from the MAM
    Before sending request, performs a number of checks
        - The resource exists
        - The record exists on that resource
        - And the image exists on that record

    :param context:
    :param data_dict:

    '''

    # Validate the data
    context = {
        u'user': toolkit.c.user or toolkit.c.author
        }
    schema = context.get(u'schema', nhm_schema.download_original_image_schema())
    data_dict, errors = toolkit.validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    # Get the resource
    resource = toolkit.get_action(u'resource_show')(context,
                                                    {
                                                        u'id': data_dict[u'resource_id']
                                                        })

    # Retrieve datastore record
    search_result = toolkit.get_action(u'datastore_search')(context, {
        u'resource_id': data_dict[u'resource_id'],
        u'filters': {
            u'_id': data_dict[u'record_id']
            }
        })

    try:
        record = search_result[u'records'][0]
    except IndexError:
        # If we don't have a result, raise not found
        raise toolkit.ObjectNotFound

    if not _image_exists_on_record(resource, record, data_dict[u'asset_id']):
        raise toolkit.ObjectNotFound

    try:
        mam_media_request(data_dict[u'asset_id'], data_dict[u'email'])
    except Exception, e:
        log.error(e)
        raise ActionError(u'Could not request original')
    else:
        return u'Original image request successful'


def object_rdf(context, data_dict):
    '''Get record RDF

    :param context:
    :param data_dict:

    '''

    # Validate the data
    context = {
        u'user': toolkit.c.user or toolkit.c.author
        }
    schema = context.get(u'schema', nhm_schema.object_rdf_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)
    # Raise any validation errors
    if errors:
        raise toolkit.ValidationError(errors)

    # get the record
    version = data_dict.get(u'version', None)
    record_dict, resource_dict = get_record_by_uuid(data_dict[u'uuid'], version)
    if record_dict:
        serializer = ObjectSerializer()
        output = serializer.serialize_record(record_dict, resource_dict, data_dict.get(u'format'),
                                             version)
        return output
    raise toolkit.ObjectNotFound


def _image_exists_on_record(resource, record, asset_id):
    '''Check the image belongs to the record

    :param resource:
    :param asset_id:
    :param record:

    '''
    # FIXME - If no image field use gallery
    image_field = resource.get(u'_image_field', None)

    # Check the asset ID belongs to the record
    for image in record[image_field]:
        url = image.get(u'identifier', None)
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
    schema = context.get(u'schema', nhm_schema.get_permanent_url_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    # extract the request parameters
    field = data_dict[u'field']
    value = data_dict[u'value']
    include_version = data_dict.get(u'include_version', False)

    # create a search dict to use with the datastore_search action
    search_dict = {
        u'resource_id': helpers.get_specimen_resource_id(),
        u'filters': {
            field: value
        },
        u'limit': 1,
    }
    result = toolkit.get_action(u'datastore_search')(context, search_dict)
    records = result[u'records']
    total = result[u'total']
    if total == 0:
        raise toolkit.ValidationError({
            u'message': u'No records found matching the given criteria',
            u'total': total,
        })
    elif total > 1:
        raise toolkit.ValidationError({
            u'message': u'More than 1 record found matching the given criteria',
            u'total': total,
        })
    else:
        uuid = records[0][u'occurrenceID']
        if include_version:
            # figure out the latest rounded version of the specimen resource data
            version = toolkit.get_action(u'datastore_get_rounded_version')(context, {
                u'resource_id': helpers.get_specimen_resource_id()
            })
            # create a path with the version included
            path = toolkit.url_for(u'object_view_versioned', uuid=uuid, version=version)
        else:
            path = toolkit.url_for(u'object_view', uuid=uuid)

        # concatenate the path with the site url and return
        return u'{}{}'.format(toolkit.config.get(u'ckan.site_url'), path)
