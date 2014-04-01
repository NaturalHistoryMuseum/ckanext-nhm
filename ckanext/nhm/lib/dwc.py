#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
from rdflib import Graph, RDF, RDFS, Namespace, URIRef

from rdflib.namespace import DCTERMS

class DwC(object):

    g = Graph()
    g.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'dwcterms.rdf'))

    DWC = Namespace('http://rs.tdwg.org/dwc/terms/')
    DWCA = Namespace('http://rs.tdwg.org/dwc/terms/attributes/')

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

    def get_term(self, name):
        """
        Get a DwC term definition
        """
        if name in ['created', 'modified']:
            return {
                'uri': URIRef(DCTERMS.term(name)),
                'group': None,
                'label': name.title()
            }

        try:
            # Find the subject in the graph
            s, p, o = self.g.triples((URIRef(self.DWC.term(name)), RDF.type, RDF.Property)).next()

            # And return a dictionary of key terms
            return {
                'uri': s,
                'group': self.g.value(s, self.DWCA.organizedInClass),
                'label': self.g.label(s).value
            }

        except StopIteration:
            raise AttributeError('Unknown DwC term: %s' % name)

    def get_group_terms(self, group):

        """Generator returning terms in a particular group
        @param group:
        @return: dict
        """

        if not isinstance(group, URIRef):
            group = URIRef(self.DWC.term(group))

        for name, term in self.__dict__.items():

            if term['group'] == group:
                yield name, term