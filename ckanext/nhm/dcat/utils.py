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
    if version is None:
        return toolkit.url_for(u'object_view', action=u'view', uuid=uuid, qualified=True)
    else:
        return toolkit.url_for(u'object_view_versioned', action=u'view', uuid=uuid, version=version,
                               qualified=True)


def rdf_resources():
    '''
    Return list of resource IDs with RDF records
    :return:
    '''
    # FIXME - Need to add in indexlots and artefacts
    return [get_specimen_resource_id()]


def as_dwc_list(objects):
    '''
    Returns the given objects as a list using the DwC standard | style separator.

    :param objects: the objects
    :return: a | separated string
    '''
    return u' | '.join(objects)


def epoch_to_datetime(epoch_timestamp):
    '''
    Converts the given epoch timestamp into a datetime object. The timestamp passed in is assumed to
    be the integer number of milliseconds since the UNIX epoch.

    :param epoch_timestamp: the integer number of milliseconds since the UNIX epoch
    :return: a datetime object
    '''
    return datetime.fromtimestamp(epoch_timestamp / 1000.0)


class Namespaces:
    '''
    Class representing the namespaces available to an RDF graph.
    '''

    def __init__(self, graph):
        '''
        :param graph: the graph object to bind the used namespaces to
        '''
        self.graph = graph

        self.bound = set()
        self.known_namespaces = {
            u'adms': namespace.Namespace(u'http://www.w3.org/ns/adms#'),
            u'aiiso': namespace.Namespace(u'http://purl.org/vocab/aiiso/schema#'),
            u'cc': namespace.Namespace(u'http://creativecommons.org/ns#'),
            u'dc': namespace.DCTERMS,
            u'dcat': namespace.Namespace(u'http://www.w3.org/ns/dcat#'),
            u'dqv': namespace.Namespace(u'http://www.w3.org/ns/dqv#'),
            u'dwc': namespace.Namespace(u'http://rs.tdwg.org/dwc/terms/'),
            u'foaf': namespace.FOAF,
            u'locn': namespace.Namespace(u'http://www.w3.org/ns/locn#'),
            u'gsp': namespace.Namespace(u'http://www.opengis.net/ont/geosparql#'),
            u'mads': namespace.Namespace(u'http://www.loc.gov/mads/rdf/v1#'),
            u'org': namespace.Namespace(u'http://www.w3.org/TR/vocab-org/#'),
            u'owl': namespace.OWL,
            u'rdf': namespace.RDF,
            u'rdfs': namespace.RDFS,
            u'schema': namespace.Namespace(u'http://schema.org/'),
            u'sdmx_code': namespace.Namespace(u'http://purl.org/linked-data/sdmx/2009/code#'),
            u'sdwc': namespace.Namespace(u'http://rs.tdwg.org/dwc/xsd/simpledarwincore#'),
            u'skos': namespace.SKOS,
            u'tdwgi': namespace.Namespace(u'http://rs.tdwg.org/ontology/voc/Institution#'),
            u'time': namespace.Namespace(u'http://www.w3.org/2006/time'),
            u'vcard': namespace.Namespace(u'http://www.w3.org/2006/vcard/ns#'),
            u'void': namespace.VOID,
            }

    def __getattr__(self, prefix):
        '''
        Returns the namespace associated with the given prefix and ensures it is bound to the graph
        if it hasn't been already.

        :param prefix: the namespace prefix as defined in the known_namespaces dict attribute
        :return: the namespace object
        '''
        if prefix in self.known_namespaces:
            ns = self.known_namespaces[prefix]
            if (prefix, ns) not in self.bound:
                self.graph.bind(prefix, ns)
                self.bound.add((prefix, ns))
            return ns
        else:
            # if you get this error, just add it above!
            raise ValueError(u'No known namespace with prefix {}'.format(prefix))
