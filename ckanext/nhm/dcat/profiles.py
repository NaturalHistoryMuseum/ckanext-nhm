# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import rdflib
from ckanext.dcat.profiles import RDFProfile
from ckanext.dcat.utils import catalog_uri, resource_uri
from rdflib import BNode, Literal, OWL, URIRef
from rdflib.namespace import FOAF, Namespace, RDF, SKOS, XSD

from ckan.plugins import toolkit

ADMS = Namespace(u'http://www.w3.org/ns/adms#')
AIISO = Namespace(u'http://purl.org/vocab/aiiso/schema#')
CC = Namespace(u'http://creativecommons.org/ns#')
DC = Namespace('http://purl.org/dc/terms/')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
DQV = Namespace(u'http://www.w3.org/ns/dqv#')
DWC = Namespace(u'http://rs.tdwg.org/dwc/terms/')
LOCN = Namespace(u'http://www.w3.org/ns/locn#')
GSP = Namespace(u'http://www.opengis.net/ont/geosparql#')
MADS = Namespace(u'http://www.loc.gov/mads/rdf/v1#')
ORG = Namespace(u'http://www.w3.org/TR/vocab-org/#')
SCHEMA = Namespace(u'http://schema.org/')
SDMX_CODE = Namespace('http://purl.org/linked-data/sdmx/2009/code#')
SDWC = Namespace(u'http://rs.tdwg.org/dwc/xsd/simpledarwincore#')
TDWGI = Namespace(u'http://rs.tdwg.org/ontology/voc/Institution#')
TIME = Namespace(u'http://www.w3.org/2006/time')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
VOID = Namespace(u'http://rdfs.org/ns/void#')

METADATA_LICENCE = u'http://creativecommons.org/publicdomain/zero/1.0/'


class NHMDCATProfile(RDFProfile):
    '''
    An RDF profile for the NHM

    http://www.w3.org/2011/gld/wiki/Data_Catalog_Vocabulary/Recipes
    http://rdf-vocabulary.ddialliance.org/discovery.html
    '''

    def _get_update_frequency_code(self, frequency):
        freq_codes = {
            u'daily': u'D',
            u'weekly': u'W',
            u'monthly': u'M',
            u'quarterly': u'Q',
            u'annual': u'A',
            }
        try:
            return u'freq-%s' % freq_codes[frequency]
        except KeyError:
            return None

    @staticmethod
    def user_uri(id):
        return u'{0}/user/{1}'.format(catalog_uri().rstrip('/'), id)

    def get_context(self):
        '''
        Set up context
        :return: context dict
        '''
        user = toolkit.get_action(u'get_site_user')({
            u'ignore_auth': True
            }, {})
        context = {
            u'user': user[u'name']
            }
        return context

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        namespaces = {
            u'dc': DC,
            u'dcat': DCAT,
            u'adms': ADMS,
            u'vcard': VCARD,
            u'foaf': FOAF,
            u'schema': SCHEMA,
            u'time': TIME,
            u'skos': SKOS,
            u'locn': LOCN,
            u'gsp': GSP,
            u'owl': OWL,
            u'tdwgi': TDWGI,
            u'aiiso': AIISO,
            u'mads': MADS,
            u'void': VOID,
            u'cc': CC,
            u'org': ORG
            }

        g = self.g

        context = self.get_context()

        # Add some more namespaces
        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        # Add #dataset to the dataset URI to denote the conceptual object - the actual dataset
        # Without #dataset is the metadata - and that needs CC0 for BBC res
        dataset_uri = URIRef(dataset_ref + u'#dataset')

        # Add dataset description (NB: This isn't the dataset - this is the dataset metadata)
        dataset_metadata_uri = URIRef(dataset_ref)
        g.add((dataset_metadata_uri, RDF.type, VOID.DatasetDescription))
        g.add((dataset_metadata_uri, CC.license, URIRef(METADATA_LICENCE)))
        # This metadata describes #dataset
        g.add((dataset_metadata_uri, FOAF.primaryTopic, dataset_uri))
        # If it is possible to access the RDF via dataset name, not uuid
        # In which case add a sameAs for the dataset name uri
        if dataset_dict[u'name'] in toolkit.request.environ.get(u'CKAN_CURRENT_URL'):
            alt_dataset_uri = u'{0}/dataset/{1}'.format(catalog_uri().rstrip('/'),
                                                        dataset_dict[u'name'])
            # Add a sameAs link
            g.add((dataset_metadata_uri, OWL.sameAs, URIRef(alt_dataset_uri)))
        # And now we can describe the dataset itself
        g.add((dataset_uri, RDF.type, DCAT.Dataset))

        # Basic fields
        items = [
            (u'title', DC.title, None, Literal),
            (u'url', DCAT.landingPage, None, URIRef),
            ]
        self._add_triples_from_dict(dataset_dict, dataset_uri, items)

        if dataset_dict.get(u'notes', None):
            g.add((dataset_uri, DCAT.description, Literal(dataset_dict[u'notes'])))

        # Add DOI
        doi = dataset_dict.get(u'doi', None)
        if doi:
            g.set((dataset_uri, DC.identifier, URIRef(doi)))

        # Tags
        for tag in dataset_dict.get(u'tags', []):
            g.add((dataset_uri, DCAT.keyword, Literal(tag[u'name'])))

        # Dates
        items = [
            (u'issued', DC.issued, [u'metadata_created'], Literal),
            (u'modified', DC.modified, [u'metadata_modified'], Literal),
            ]
        self._add_date_triples_from_dict(dataset_dict, dataset_uri, items)

        # We don't have maintainers - whoever added it to the portal is the maintainer
        creator_user_id = dataset_dict[u'creator_user_id']
        user = toolkit.get_action(u'user_show')(context, {
            u'id': creator_user_id,
            })

        # Add publisher
        nhm_uri = self.graph_add_museum()

        if user:
            # if this is the admin user, just add the contactPoint
            if user[u'sysadmin'] and user[u'name'] == u'admin':
                g.add((dataset_uri, DCAT.contactPoint, nhm_uri))
            else:
                user_uri = URIRef(self.user_uri(creator_user_id))
                g.add((user_uri, RDF.type, VCARD.Person))
                if u'fullname' in user:
                    g.add((user_uri, VCARD.fn, Literal(user[u'fullname'])))
                if u'email' in user:
                    g.add((user_uri, VCARD.hasEmail, URIRef(user[u'email'])))
                # All users are members of the NHM
                g.add((user_uri, MADS.hasAffiliation, nhm_uri))
                # This user is the contact point for the dataset
                g.add((dataset_uri, DCAT.contactPoint, user_uri))

        # Add update frequency
        update_frequency = dataset_dict.get(u'update_frequency', None)
        if update_frequency:
            code = self._get_update_frequency_code(update_frequency)
            if code:
                g.set((dataset_uri, DC.accrualPeriodicity, URIRef(SDMX_CODE[code])))

        # Add licence - use URL if we have it
        # Otherwise try using the licence title
        if dataset_dict.get(u'license_url', None):
            g.set((dataset_uri, DC.license, URIRef(dataset_dict[u'license_url'])))
        elif dataset_dict.get(u'license_title', None):
            g.set((dataset_uri, DC.license, Literal(dataset_dict[u'license_title'])))

        # Add categories
        # Create concept schema for all categories, add link any related to the dataset
        for category in dataset_dict[u'dataset_category']:
            # print category
            n = BNode()
            g.add((n, rdflib.RDF.type, SKOS.Concept))
            g.add((n, SKOS.prefLabel, Literal(category)))
            g.add((dataset_uri, DCAT.theme, n))

        # Temporal extent
        temporal_extent = dataset_dict.get(u'temporal_extent', None)
        if temporal_extent:
            g.add((dataset_uri, DC.temporal, Literal(temporal_extent)))

        author = dataset_dict.get(u'author', None)
        if author:

            if author == u'Natural History Museum':
                g.add((dataset_uri, DC.creator, nhm_uri))
            else:
                author_details = BNode()
                g.add((author_details, VCARD.fn, Literal(author)))
                if dataset_dict.get(u'author_email', None):
                    g.add((author_details, VCARD.hasEmail, Literal(dataset_dict[u'author_email'])))
                g.add((author_details, RDF.type, VCARD.Person))
                g.add((dataset_uri, DC.creator, author_details))
                affiliation = dataset_dict.get(u'affiliation', None)
                if affiliation:
                    if affiliation == u'Natural History Museum':
                        g.add((author_details, MADS.hasAffiliation, nhm_uri))
                    else:
                        g.add((author_details, MADS.hasAffiliation, Literal(affiliation)))

        contributors = dataset_dict.get(u'contributors', None)
        if contributors:
            g.add((dataset_uri, DC.contributor, Literal(contributors)))

        self.graph_add_resources(dataset_uri, dataset_dict)

    def graph_add_museum(self):
        g = self.g
        nhm_uri = URIRef(u'http://nhm.ac.uk')
        g.add((nhm_uri, RDF.type, ORG.Organization))
        g.add((nhm_uri, RDF.type, FOAF.Organization))
        # Update the name
        g.set((nhm_uri, FOAF.name, Literal(u'Natural History Museum')))
        # # Add TDWG institution details - http://rs.tdwg.org/ontology/voc/Institution
        g.set((nhm_uri, TDWGI.acronymOrCoden, Literal(u'NHMUK')))
        g.set((nhm_uri, TDWGI.institutionType,
               URIRef(u'http://rs.tdwg.org/ontology/voc/InstitutionType#museum')))
        # Add AIISO institution
        g.add((nhm_uri, RDF.type, AIISO.Institution))
        # Add same as link
        g.add((nhm_uri, OWL.sameAs, URIRef(u'http://dbpedia.org/resource/Natural_history_museum')))
        g.add((nhm_uri, OWL.sameAs, URIRef(u'https://www.wikidata.org/wiki/Q309388')))
        return nhm_uri

    def graph_add_resources(self, dataset_uri, dataset_dict):
        g = self.g

        for resource_dict in dataset_dict.get(u'resources', []):

            distribution = URIRef(resource_uri(resource_dict))

            g.add((dataset_uri, DCAT.distribution, distribution))

            # As we don't allow direct download of the data, we need to add landing page
            # To dataset - see http://www.w3.org/TR/vocab-dcat/#example-landing-page
            g.add((dataset_uri, DCAT.landingPage, distribution))

            g.add((distribution, RDF.type, DCAT.Distribution))

            #  Simple values
            items = [
                (u'name', DC.title, None, Literal),
                (u'description', DC.description, None, Literal),
                (u'status', ADMS.status, None, Literal),
                (u'rights', DC.rights, None, Literal),
                (u'license', DC.license, None, Literal),
                ]

            self._add_triples_from_dict(resource_dict, distribution, items)

            # Format
            if '/' in resource_dict.get(u'format', u''):
                g.add((distribution, DCAT.mediaType,
                       Literal(resource_dict[u'format'])))
            else:
                if resource_dict.get(u'format'):
                    g.add((distribution, DC[u'format'],
                           Literal(resource_dict[u'format'])))

                if resource_dict.get(u'mimetype'):
                    g.add((distribution, DCAT.mediaType,
                           Literal(resource_dict[u'mimetype'])))

            g.set((distribution, DCAT.accessURL, distribution))

            # Dates
            items = [
                (u'issued', DC.issued, None, Literal),
                (u'modified', DC.modified, None, Literal),
                ]

            self._add_date_triples_from_dict(resource_dict, distribution, items)

            # Numbers
            if resource_dict.get(u'size'):
                try:
                    g.add((distribution, DCAT.byteSize,
                           Literal(float(resource_dict[u'size']),
                                   datatype=XSD.decimal)))
                except (ValueError, TypeError):
                    g.add((distribution, DCAT.byteSize,
                           Literal(resource_dict[u'size'])))
