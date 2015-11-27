#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from rdflib import URIRef, BNode, Literal
from ckanext.dcat.processors import RDFSerializer as DCATRDFSerializer
from ckanext.dcat.utils import catalog_uri, dataset_uri, url_to_rdflib_format
from ckanext.nhm.dcat.utils import record_uri

class RDFSerializer(DCATRDFSerializer):

    def serialize_record(self, dataset_dict, _format='xml'):
        '''
        Given a CKAN dataset dict, returns an RDF serialization

        The serialization format can be defined using the `_format` parameter.
        It must be one of the ones supported by RDFLib, defaults to `xml`.

        Returns a string with the serialized dataset
        '''

        self.graph_from_record(dataset_dict)

        _format = url_to_rdflib_format(_format)

        if _format == 'json-ld':
            output = self.g.serialize(format=_format, auto_compact=True)
        else:
            output = self.g.serialize(format=_format)

        return output

    def graph_from_catalog(self, catalog_dict=None):
        '''
        Creates a graph for the catalog (CKAN site) using the loaded profiles

        The class RDFLib graph (accessible via `serializer.g`) will be updated
        by the loaded profiles.

        Returns the reference to the catalog, which will be an rdflib URIRef.
        '''

        record_ref = URIRef(record_uri())

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            profile.graph_from_record(catalog_dict, record_ref)

        return record_ref

