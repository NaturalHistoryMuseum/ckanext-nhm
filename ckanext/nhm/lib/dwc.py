# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict

from importlib_resources import files
from lxml import etree

# even though we use simple DwC terms, we use this XSD as it allows us to group terms into events
# etc., on record display
path = files('ckanext.nhm.src').joinpath('tdwg_dwcterms.xsd')
with open(path, 'r') as xml_f:
    data = etree.parse(xml_f, etree.XMLParser())
    DWC_XSD = data.getroot()


def dwc_terms(fields):
    """
    Get DwC terms and groups, parsed from tdwg_dwcterms. Even though we use simple DwC
    terms, we use this XSD as it allows us to group terms into events etc., on record
    display.

    :param fields: list of fields for this record
    :return: dict, keyed by groups
    """
    fields = list(fields)
    dynamic_properties_uri = None
    terms = OrderedDict()
    for group in DWC_XSD.iterfind('xs:group', namespaces=DWC_XSD.nsmap):
        for element in group.iterfind(
            'xs:sequence/xs:element', namespaces=DWC_XSD.nsmap
        ):
            ns, name = element.get('ref').split(':')
            uri = f'{DWC_XSD.nsmap[ns]}{name}'
            if name == 'dynamicProperties':
                # Keep a references to the dynamic properties uri, we
                # will need this later on
                dynamic_properties_uri = uri
            if name in fields:
                # We have a field for this group -
                # so create the group if it doesn't exist
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

    # dynamic properties are actually part of RecordLevelTerms, but we treat it slightly differently
    # - filter out all hidden fields (starting with _)
    terms['dynamicProperties'] = {
        dynamic_properties_uri: [f for f in fields if not f.startswith('_')]
    }

    return terms
