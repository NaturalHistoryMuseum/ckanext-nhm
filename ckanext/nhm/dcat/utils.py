# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.nhm.lib.helpers import get_specimen_resource_id
from datetime import datetime
from rdflib import namespace

from ckan.plugins import toolkit


def object_uri(uuid, version=None):
    '''
    Returns an URI for an object
    :return:
    '''
    return toolkit.url_for('object.view', uuid=uuid, version=version, qualified=True)


def rdf_resources():
    '''
    Return list of resource IDs with RDF records
    :return:
    '''
    # FIXME - Need to add in indexlots and artefacts
    return [get_specimen_resource_id()]


def as_dwc_list(objects):
    """
    Returns the given objects as a list using the DwC standard | style separator.

    :param objects: the objects
    :return: a | separated string
    """
    return ' | '.join(objects)


def epoch_to_datetime(epoch_timestamp):
    """
    Converts the given epoch timestamp into a datetime object. The timestamp passed in
    is assumed to be the integer number of milliseconds since the UNIX epoch.

    :param epoch_timestamp: the integer number of milliseconds since the UNIX epoch
    :return: a datetime object
    """
    return datetime.fromtimestamp(epoch_timestamp / 1000.0)


class Namespaces:
    """
    Class representing the namespaces available to an RDF graph.
    """

    def __init__(self, graph):
        '''
        :param graph: the graph object to bind the used namespaces to
        '''
        self.graph = graph

        self.bound = set()
        self.known_namespaces = {
            'adms': namespace.Namespace('http://www.w3.org/ns/adms#'),
            'aiiso': namespace.Namespace('http://purl.org/vocab/aiiso/schema#'),
            'cc': namespace.Namespace('http://creativecommons.org/ns#'),
            'dc': namespace.DCTERMS,
            'dcat': namespace.Namespace('http://www.w3.org/ns/dcat#'),
            'dqv': namespace.Namespace('http://www.w3.org/ns/dqv#'),
            'dwc': namespace.Namespace('http://rs.tdwg.org/dwc/terms/'),
            'foaf': namespace.FOAF,
            'locn': namespace.Namespace('http://www.w3.org/ns/locn#'),
            'gsp': namespace.Namespace('http://www.opengis.net/ont/geosparql#'),
            'mads': namespace.Namespace('http://www.loc.gov/mads/rdf/v1#'),
            'org': namespace.Namespace('http://www.w3.org/TR/vocab-org/#'),
            'owl': namespace.OWL,
            'rdf': namespace.RDF,
            'rdfs': namespace.RDFS,
            'schema': namespace.Namespace('http://schema.org/'),
            'sdmx_code': namespace.Namespace(
                'http://purl.org/linked-data/sdmx/2009/code#'
            ),
            'sdwc': namespace.Namespace('http://rs.tdwg.org/dwc/xsd/simpledarwincore#'),
            'skos': namespace.SKOS,
            'tdwgi': namespace.Namespace(
                'http://rs.tdwg.org/ontology/voc/Institution#'
            ),
            'time': namespace.Namespace('http://www.w3.org/2006/time'),
            'vcard': namespace.Namespace('http://www.w3.org/2006/vcard/ns#'),
            'void': namespace.VOID,
        }

    def __getattr__(self, prefix):
        """
        Returns the namespace associated with the given prefix and ensures it is bound
        to the graph if it hasn't been already.

        :param prefix: the namespace prefix as defined in the known_namespaces dict attribute
        :return: the namespace object
        """
        if prefix in self.known_namespaces:
            ns = self.known_namespaces[prefix]
            if (prefix, ns) not in self.bound:
                self.graph.bind(prefix, ns)
                self.bound.add((prefix, ns))
            return ns
        else:
            # if you get this error, just add it above!
            raise ValueError(f'No known namespace with prefix {prefix}')
