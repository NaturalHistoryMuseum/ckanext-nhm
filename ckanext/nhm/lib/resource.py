#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import json
import ckan.logic as logic


NotFound = logic.NotFound


def resource_get_ordered_fields(resource_id):
    """
    This is a replacement for resource_view_get_fields, but this function
    handles errors internally, and return the fields in their original order
    @param resource_id:
    @return:
    """

    print(resource_id)

    # data = {'resource_id': resource_id, 'limit': 0}
    # try:
    #     result = toolkit.get_action('datastore_search')({}, data)
    # except NotFound:
    #     return []
    #
    # return [field['id'] for field in result.get('fields', [])]

    return []



