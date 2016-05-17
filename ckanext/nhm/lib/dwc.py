#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from lxml import etree
import sys
import os
from collections import OrderedDict

def dwc_terms(fields):
    """
    Get DwC terms and groups, parsed from tdwg_dwcterms
    :return: dict, keyed by groups
    :param fields: list of fields for this record
    :return:
    """

    # Even though we use simple DwC terms, we use this XSD as it allows
    # us to group terms into events etc., on record display
    f = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src/tdwg_dwcterms.xsd')

    data = etree.parse(open(f), etree.XMLParser())
    root = data.getroot()

    dynamic_properties_uri = None
    terms = OrderedDict()
    for group in root.iterfind("xs:group", namespaces=root.nsmap):
        for element in group.iterfind("xs:sequence/xs:element", namespaces=root.nsmap):
            ns, name = element.get("ref").split(':')
            uri = '{ns}{name}'.format(ns=root.nsmap[ns], name=name)
            if name == 'dynamicProperties':
                # Keep a references to the dynamic properties uri, we
                # will need this later on
                dynamic_properties_uri = uri
            if name in fields:
                # We have a field for this group - so create the group if it doesn't exist
                # We do this here, so we
                try:
                    terms[group.get('name')]
                except KeyError:
                    terms[group.get('name')] = OrderedDict()

                terms[group.get('name')][uri] = name
                # Remove field name from the fields list - those remaining will
                # be dynamic properties
                fields.remove(name)

    # Add created - not actually in DwC
    terms['RecordLevelTerms']['http://purl.org/dc/terms/created'] = 'created'

    # Dynamic properties are actually part of RecordLevelTerms, but we
    # treat it slightly differently - filter out all hidden fields (starting with _)
    terms['dynamicProperties'] = {
        dynamic_properties_uri: [f for f in fields if not f.startswith('_')]
    }

    return terms