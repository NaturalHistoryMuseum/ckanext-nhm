#!/usr/bin/env python
# encoding: utf-8
from lxml import etree
import os
from collections import OrderedDict


# even though we use simple DwC terms, we use this XSD as it allows us to group terms into events
# etc., on record display
path = os.path.join(os.path.dirname(os.path.dirname(__file__)), u'src/tdwg_dwcterms.xsd')
with open(path, u'r') as xml_f:
    data = etree.parse(xml_f, etree.XMLParser())
    DWC_XSD = data.getroot()


def dwc_terms(fields):
    """
    Get DwC terms and groups, parsed from tdwg_dwcterms
    :return: dict, keyed by groups
    :param fields: list of fields for this record
    :return:
    """
    dynamic_properties_uri = None
    terms = OrderedDict()
    for group in DWC_XSD.iterfind(u'xs:group', namespaces=DWC_XSD.nsmap):
        for element in group.iterfind(u'xs:sequence/xs:element', namespaces=DWC_XSD.nsmap):
            ns, name = element.get(u'ref').split(u':')
            uri = u'{ns}{name}'.format(ns=DWC_XSD.nsmap[ns], name=name)
            if name == u'dynamicProperties':
                # Keep a references to the dynamic properties uri, we
                # will need this later on
                dynamic_properties_uri = uri
            if name in fields:
                # We have a field for this group - so create the group if it doesn't exist
                # We do this here, so we
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

    # dynamic properties are actually part of RecordLevelTerms, but we treat it slightly differently
    # - filter out all hidden fields (starting with _)
    terms[u'dynamicProperties'] = {
        dynamic_properties_uri: [f for f in fields if not f.startswith(u'_')]
    }

    return terms
