#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
from rdflib import Graph, RDF, Namespace, URIRef

from rdflib.namespace import DCTERMS
from collections import OrderedDict

# Darwin core namespaces
DWC = Namespace('http://rs.tdwg.org/dwc/terms/')
DWCA = Namespace('http://rs.tdwg.org/dwc/terms/attributes/')

class DwC(object):

    g = Graph()
    g.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'dwcterms.rdf'))

    # Create list of DwC properties on the same order as rdf graph
    terms = []
    for p in g.subjects(RDF.type, RDF.Property):
        terms.append(p)

    # TODO: Write test to ensure groups match
    groups = OrderedDict([
                (DWC.all, 'Specimen'),
                (DWC.Taxon, 'Taxonomy'),
                (DWC.Event, 'Event'),
                (DCTERMS.Location, 'Location'),
                (DWC.Identification, 'Identification'),
                (DWC.Occurrence, 'Occurrence'),
                (DWC.ResourceRelationship, 'Relationship'),
                (DWC.GeologicalContext, 'Geology')
            ])

    __dict__ = {}

    def __init__(self, **kwargs):

        # Set all the initial values
        for name, value in kwargs.items():
            self[name] = value

    def __setitem__(self, name, value):

        # On setting a value, get the DwC term properties
        if not name.startswith('_'):
            term = self.get_term(name)
            term['value'] = value
            self.__dict__[name] = term

    def __getitem__(self, name):
        return self.__dict__[name]

    def get_groups(self):
        """
        @return: Generator of group names
        """
        for group_uri, group in self.groups.items():
            yield group_uri, group

    def get_term(self, name):
        """
        Get a DwC term definition
        """

        # DC Terms are not included in RDF file, so handle separately
        dc = ['created', 'modified']

        if name in dc:
            return {
                'uri': URIRef(DCTERMS.term(name)),
                'group': None,
                'label': name.title(),
                'index': 0 - dc.index(name)  # Create a -x index so doesn't clash with DwC
            }

        try:

            # We want to keep track of the index, so we can order the fields as per DwC standard
            i = self.terms.index(DWC.term(name))
            s = self.terms[i]

            # And return a dictionary of key terms
            return {
                'uri': s,
                'group': self.g.value(s, DWCA.organizedInClass),
                'label': self.g.label(s).value,
                'index': i
            }

        except ValueError:
            raise ValueError('Unknown DwC term: %s' % name)

    def get_group_terms(self, group):

        """ Return dictionary of terms in a group, using index for key
        @param group:
        @return: dict
        """
        terms = {}

        if not isinstance(group, URIRef):
            group = URIRef(DWC.term(group))

        for term in self.__dict__.values():

            if term['group'] == group:
                terms[term['index']] = term

        print sorted(terms)

        return terms