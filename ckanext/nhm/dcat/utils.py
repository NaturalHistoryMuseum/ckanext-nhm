#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from ckanext.dcat.utils import catalog_uri

def object_uri(record_dict):
    """
    Returns an URI for an object

    This will be used to uniquely reference the dataset on the RDF
    serializations.

    Returns a string with the dataset URI.
    """

    uuid = record_dict.get('uuid')
    uri = '{0}/object/{1}'.format(catalog_uri().rstrip('/'), uuid)
    return uri