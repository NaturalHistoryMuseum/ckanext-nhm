#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict

import os
from lxml import etree


def dwc_terms(fields):
    '''Get DwC terms and groups, parsed from tdwg_dwcterms. Even though we use simple
    DwC terms, we use this XSD as it allows us to group terms into events etc.,
    on record display.

    :param fields: list of fields for this record

    :returns: dict, keyed by groups

    '''

    f = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     u'src/tdwg_dwcterms.xsd')

    data = etree.parse(open(f), etree.XMLParser())
    root = data.getroot()

    dynamic_properties_uri = None
    terms = OrderedDict()
    for group in root.iterfind(u'xs:group', namespaces=root.nsmap):
        for element in group.iterfind(u'xs:sequence/xs:element', namespaces=root.nsmap):
            ns, name = element.get(u'ref').split(u':')
            uri = u'{ns}{name}'.format(ns=root.nsmap[ns], name=name)
            if name == u'dynamicProperties':
                # Keep a references to the dynamic properties uri, we
                # will need this later on
                dynamic_properties_uri = uri
            if name in fields:
                # We have a field for this group -
                # so create the group if it doesn't exist
                try:
                    terms[group.get(u'name')]
                except KeyError:
                    terms[group.get(u'name')] = OrderedDict()

                terms[group.get(u'name')][uri] = name
                # Remove field name from the fields list - those remaining will
                # be dynamic properties
                fields.remove(name)

    # Add created - not actually in DwC
    terms[u'RecordLevelTerms'][u'http://purl.org/dc/terms/created'] = u'created'

    # Dynamic properties are actually part of RecordLevelTerms, but we
    # treat it slightly differently - filter out all hidden fields (starting with _)
    terms[u'dynamicProperties'] = {
        dynamic_properties_uri: [f for f in fields if not f.startswith(u'_')]
        }

    return terms
