#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import json
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import request, response

NotFound = logic.NotFound

# Filter used for filter groups
FIELD_DISPLAY_FILTER = '_f'

# Name of the field display cookie for sotring hidden fields
HIDDEN_FIELDS_COOKIE_NAME = 'hidden_fields'


def resource_get_ordered_fields(resource_id):
    """
    This is a replacement for resource_view_get_fields, but this function
    handles errors internally, and return the fields in their original order
    @param resource_id:
    @return:
    """
    data = {'resource_id': resource_id, 'limit': 0}
    try:
        result = toolkit.get_action('datastore_search')({}, data)
    except NotFound:
        return []

    return [field['id'] for field in result.get('fields', [])]


def resource_filter_options(resource):
    """
    Return the list of filter options for the given resource.

    Note that this is the master source for the list of available options.

    We may want to have this dependent on available fields (rather than
    resource format), so it's useful to keep this as a function (rather
    than a static dict).

    @type resource: dict
    @param resource: Dictionary representing a resource
    @rtype: dict
    @return: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - sql: Optional. The SQL WHERE statement to use when this
                       option is checked (as a tuple containing statement
                       and value replacements);
                - sql_false: Optional. The SQL WHERE statement to use when
                             this option is unchecked (as a tuple containing
                             statement and value replacements).
    """
    table = resource['id']
    # Get the resource-dependent filter option list
    if resource['format'].lower() == 'dwc':
        return {
            '_has_type': {
                'label': 'Has type',
                'sql': ('"{}"."typeStatus" IS NOT NULL'.format(table),)
            },
            '_has_image': {
                'label': 'Has image',
                'sql': ('"{}"."associatedMedia" IS NOT NULL'.format(table),)
            },
            '_has_lat_long': {
                'label': 'Has lat/long',
                 # BS: Changed to look for latitude field,as _geom is only available after a map has been added
                 # As this works for all DwC, we might get datasets without a map
                'sql': ('"{}"."decimalLatitude" IS NOT NULL'.format(table),)
            },
            '_exclude_centroid': {
                'label': 'Exclude centroids',
                'sql': ('NOT (LOWER("{}"."centroid"::text) = ANY(\'{{true,yes,1}}\'))'.format(table),)
            }
        }
    else:
        return {}


def parse_request_filters():

    """
    Get the filters from the request object
    @return:
    """
    filter_dict = {}

    try:
        filter_params = request.params.get('filters').split('|')
    except AttributeError:
        return {}

    filter_params = filter(None, filter_params)

    for filter_param in filter_params:
        field, value = filter_param.split(':', 1)

        try:
            filter_dict[field].append(value)
        except KeyError:
            filter_dict[field] = [value]

    return filter_dict


## Hidden field cookie handling

def resource_filter_get_cookie(resource_id=None):
    """
    Retrieve the resource filter cookie
    @param resource_id:
    @return:
    """
    try:
        cookie = json.loads(request.cookies[HIDDEN_FIELDS_COOKIE_NAME])
    except KeyError:
        return {}

    if resource_id:
        return cookie.get(resource_id, None)
    else:
        return cookie


def resource_filter_set_cookie(resource_id, hidden_fields):
    """
    Set the resource filter hidden fields cookie
    @param resource_id:
    @param hidden_fields:
    @return:
    """

    cookie = resource_filter_get_cookie()
    cookie[resource_id] = hidden_fields

    response.set_cookie(HIDDEN_FIELDS_COOKIE_NAME, json.dumps(cookie))


def resource_filter_delete_cookie(resource_id):
    """
    Delete the hidden fields for this resource ID
    @param resource_id:
    @return:
    """

    cookie = resource_filter_get_cookie()
    # Remove the dictionary item for this resource ID
    cookie.pop(resource_id, None)
    # And reset the cookie
    response.set_cookie(HIDDEN_FIELDS_COOKIE_NAME, json.dumps(cookie))


