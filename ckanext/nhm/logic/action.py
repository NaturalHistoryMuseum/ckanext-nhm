#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json
import logging

import ckanext.nhm.logic.schema as nhm_schema
from ckanext.nhm.dcat.processors import RDFSerializer
from ckanext.nhm.lib.mam import mam_media_request
from ckanext.nhm.lib.record import get_record_by_uuid

import ckan.logic as logic
import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def record_show(context, data_dict):
    '''Retrieve an individual record

    :param context:
    :param data_dict: 

    '''
    # Validate the data (TODO: do we need to redefine context here?)
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': toolkit.c.user or toolkit.c.author
        }
    schema = context.get(u'schema', nhm_schema.record_show_schema())
    data_dict, errors = toolkit.navl_validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    resource_id = toolkit.get_or_bust(data_dict, u'resource_id')
    record_id = toolkit.get_or_bust(data_dict, u'record_id')

    # Retrieve datastore record
    record_data_dict = {'resource_id': resource_id, 'filters': {'_id': record_id}}
    if 'version' in data_dict:
        record_data_dict['version'] = data_dict['version']
    search_result = get_action('datastore_search')(context, record_data_dict)

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
        u'model': model,
        u'session': model.Session,
        u'user': toolkit.c.user or toolkit.c.author
        }
    schema = context.get(u'schema', nhm_schema.download_original_image_schema())
    data_dict, errors = toolkit.validate(data_dict, schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    # Get the resource
    resource = toolkit.get_action(u'resource_show')(context,
                                                    {u'id': data_dict[u'resource_id']})

    # Retrieve datastore record
    search_result = toolkit.get_action(u'datastore_search')(context, {
        u'resource_id': data_dict[u'resource_id'],
        u'filters': {u'_id': data_dict[u'record_id']}
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
        raise logic.ActionError(u'Could not request original')
    else:
        return u'Original image request successful'


def object_rdf(context, data_dict):
    '''Get record RDF

    :param context:
    :param data_dict: 

    '''

    # Validate the data
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': toolkit.c.user or toolkit.c.author
        }
    schema = context.get(u'schema', nhm_schema.object_rdf_schema())
    data_dict, errors = toolkit.validate(data_dict, schema, context)
    # Raise any validation errors
    if errors:
        raise toolkit.ValidationError(errors)

    # get the record
    version = data_dict.get(u'version', None)
    record_dict, resource_dict = get_record_by_uuid(data_dict['uuid'], version)
    if record_dict:
        record_dict[u'uuid'] = data_dict[u'uuid']
        serializer = RDFSerializer()
        output = serializer.serialize_record(record_dict, resource_dict,
                                             _format=data_dict.get(u'format'))
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
        url = image.get('identifier', None)
        if asset_id in url:
            return True
    return False
