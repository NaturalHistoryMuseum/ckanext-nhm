#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.dcat.processors import RDFSerializer as DCATSerializer
from ckanext.dcat.utils import url_to_rdflib_format
from ckanext.nhm.dcat.utils import object_uri
from rdflib import URIRef


class RDFSerializer(DCATSerializer):
    '''Transforms records into RDF formats.'''

    def serialize_record(self, record_dict, resource_dict, _format=u'xml'):
        '''Given a CKAN dataset dict, returns an RDF serialization.

        :param record_dict: the record data
        :param resource_dict: the resource data
        :param _format: the serialisation format to use;
            must be supported by RDFLib (optional, default: u'xml')

        :returns: a string with the serialized dataset

        '''

        self.graph_from_record(record_dict, resource_dict)

        _format = url_to_rdflib_format(_format)

        if _format == u'json-ld':
            output = self.g.serialize(format=_format, auto_compact=True)
        else:
            output = self.g.serialize(format=_format)

        return output

    def graph_from_record(self, record_dict=None, resource=None):
        '''Creates a graph for the catalog (CKAN site) using the loaded profiles.
        
        The class RDFLib graph (accessible via `serializer.g`) will be updated
        by the loaded profiles.

        :param record_dict: the record data (optional, default: None)
        :param resource: the resource data (optional, default: None)

        :returns: the reference to the catalog, which will be an rdflib URIRef

        '''

        record_ref = URIRef(object_uri(record_dict))

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            try:
                profile.graph_from_record(record_dict, resource, record_ref)
            except AttributeError:
                continue

        return record_ref
