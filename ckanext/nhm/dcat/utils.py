#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from ckanext.dcat.utils import catalog_uri
from ckanext.nhm.lib.helpers import get_specimen_resource_id

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


def rdf_resources():
    """
    Return list of resource IDs with RDF records
    :return:
    """
    # FIXME - Need to add in indexlots and artefacts
    return [get_specimen_resource_id()]