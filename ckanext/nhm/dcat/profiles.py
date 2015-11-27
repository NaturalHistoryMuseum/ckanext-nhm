
import rdflib
from pylons import config
from rdflib.namespace import Namespace, RDF, XSD

from rdflib import URIRef, BNode, Literal
from rdflib import OWL
from rdflib.namespace import FOAF, SKOS

from ckan.plugins import toolkit
from ckan.lib.helpers import url_for
from ckanext.dcat.utils import resource_uri, publisher_uri_from_dataset_dict, dataset_uri, catalog_uri
from ckanext.dcat.profiles import RDFProfile
from ckanext.nhm.lib.helpers import dataset_categories

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SDMX_CODE = Namespace("http://purl.org/linked-data/sdmx/2009/code#")
TDWGI = Namespace('http://rs.tdwg.org/ontology/voc/Institution#')
AIISO = Namespace('http://purl.org/vocab/aiiso/schema#')
MADS = Namespace('http://www.loc.gov/mads/rdf/v1#')
VOID = Namespace('http://rdfs.org/ns/void#')
CC = Namespace('http://creativecommons.org/ns#')
ORG = Namespace('http://www.w3.org/TR/vocab-org/#')


namespaces = {
    'dct': DCT,
    'dcat': DCAT,
    'adms': ADMS,
    'vcard': VCARD,
    'foaf': FOAF,
    'schema': SCHEMA,
    'time': TIME,
    'skos': SKOS,
    'locn': LOCN,
    'gsp': GSP,
    'owl': OWL,
    'tdwgi': TDWGI,
    'aiiso': AIISO,
    'mads': MADS,
    'void': VOID,
    'cc': CC,
    'org': ORG
}

# All metadata licence under CC0
METADATA_LICENCE = 'http://creativecommons.org/publicdomain/zero/1.0'

# FIXME: dataset ID / name

class NHMDCATProfile(RDFProfile):
    '''
    An RDF profile for the NHM

    http://www.w3.org/2011/gld/wiki/Data_Catalog_Vocabulary/Recipes
    http://rdf-vocabulary.ddialliance.org/discovery.html

    '''

    def _get_update_frequency_code(self, frequency):
        freq_codes = {
            'daily': 'D',
            'weekly': 'W',
            'monthly': 'M',
            'quarterly': 'Q',
            'annual': 'A',
        }
        try:
            return 'freq-%s' % freq_codes[frequency]
        except IndexError:
            return None

    @staticmethod
    def _update_publisher(g):
        """
        Default graph uses the organisation for publisher
        Switch ours to use the nhm.ac.uk URI
        :param g:
        :return: None
        """

        # We want to change this to use the Museum URI
        new_publisher = URIRef('http://nhm.ac.uk')
        # Load the old publisher
        old_publisher = g.value(predicate=RDF.type, object=FOAF.Organization)
        # And reassign anny existing value
        for s, p, o in g.triples((old_publisher, None, None)):
            g.set((new_publisher, p, o))

        # # Load any triples where publisher is the object (for example, dataset publisher)
        for s, p, o in g.triples((None, None, old_publisher)):
            g.set((s, p, new_publisher))

        # Update the name
        g.set((new_publisher, FOAF.name, Literal('Natural History Museum')))
        # Remove the old publisher
        g.remove((old_publisher, None, None))
        # # Add TDWG institution details - http://rs.tdwg.org/ontology/voc/Institution
        g.set((new_publisher, TDWGI.acronymOrCoden, Literal('NHMUK')))
        g.set((new_publisher, TDWGI.institutionType, URIRef('http://rs.tdwg.org/ontology/voc/InstitutionType#museum')))
        # Add AIISO institution
        g.add((new_publisher, RDF.type, AIISO.Institution))
        # Add same as link
        g.add((new_publisher, OWL.sameAs, URIRef('http://dbpedia.org/resource/Natural_history_museum')))
        g.add((new_publisher, OWL.sameAs, URIRef('https://www.wikidata.org/wiki/Q309388')))

    @staticmethod
    def user_uri(id):
        return '{0}/user/{1}'.format(catalog_uri().rstrip('/'), id)

    def graph_add_resources(self, dataset_uri, dataset_dict):

        g = self.g

        for resource_dict in dataset_dict.get('resources', []):

            distribution = URIRef(resource_uri(resource_dict))

            g.add((dataset_uri, DCAT.distribution, distribution))

            # As we don't allow direct download of the data, we need to add landing page
            # To dataset - see http://www.w3.org/TR/vocab-dcat/#example-landing-page
            g.add((dataset_uri, DCAT.landingPage, distribution))

            g.add((distribution, RDF.type, DCAT.Distribution))

            #  Simple values
            items = [
                ('name', DCT.title, None),
                ('description', DCT.description, None),
                ('status', ADMS.status, None),
                ('rights', DCT.rights, None),
                ('license', DCT.license, None),
            ]

            self._add_triples_from_dict(resource_dict, distribution, items)

            # Format
            if '/' in resource_dict.get('format', ''):
                g.add((distribution, DCAT.mediaType,
                       Literal(resource_dict['format'])))
            else:
                if resource_dict.get('format'):
                    g.add((distribution, DCT['format'],
                           Literal(resource_dict['format'])))

                if resource_dict.get('mimetype'):
                    g.add((distribution, DCAT.mediaType,
                           Literal(resource_dict['mimetype'])))

            g.set((distribution, DCAT.accessURL, distribution))

            # Dates
            items = [
                ('issued', DCT.issued, None),
                ('modified', DCT.modified, None),
            ]

            self._add_date_triples_from_dict(resource_dict, distribution, items)

            # Numbers
            if resource_dict.get('size'):
                try:
                    g.add((distribution, DCAT.byteSize,
                           Literal(float(resource_dict['size']),
                                   datatype=XSD.decimal)))
                except (ValueError, TypeError):
                    g.add((distribution, DCAT.byteSize,
                           Literal(resource_dict['size'])))


    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}

        # Add some more namespaces
        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        # Add #dataset to the dataset URI to denote the conceptual object - the actual dataset
        # Without #dataset is the metadata - and that needs CC0 for BBC res
        dataset_uri = URIRef(dataset_ref + '#dataset')

        # Add dataset description (NB: This isn't the dataset - this is the dataset metadata)
        dataset_metadata_uri = URIRef(dataset_ref)
        g.add((dataset_metadata_uri, RDF.type, VOID.DatasetDescription))
        g.add((dataset_metadata_uri, CC.license, URIRef(METADATA_LICENCE)))
        # This metadata describes #dataset
        g.add((dataset_metadata_uri, FOAF.primaryTopic, dataset_uri))

        # And now we can describe the dataset itself
        g.add((dataset_uri, RDF.type, DCAT.Dataset))

        # Basic fields
        items = [
            ('title', DCT.title, None),
            ('url', DCAT.landingPage, None),
        ]
        self._add_triples_from_dict(dataset_dict, dataset_uri, items)

        if dataset_dict.get('notes', None):
            g.add((dataset_uri, DCAT.description, Literal(dataset_dict['notes'])))

        # Add DOI
        doi = dataset_dict.get('doi', None)
        if doi:
            g.set((dataset_uri, DCT.identifier, URIRef(doi)))

        # Tags
        for tag in dataset_dict.get('tags', []):
            g.add((dataset_uri, DCAT.keyword, Literal(tag['name'])))

        # Dates
        items = [
            ('issued', DCT.issued, ['metadata_created']),
            ('modified', DCT.modified, ['metadata_modified']),
        ]
        self._add_date_triples_from_dict(dataset_dict, dataset_uri, items)

        # We don't have maintainers - whoever added it to the portal is the maintainer
        creator_user_id = dataset_dict['creator_user_id']
        user = toolkit.get_action('user_show')(context, {
            'id': creator_user_id,
        })

        # Add publisher
        nhm_uri = URIRef('http://nhm.ac.uk')
        g.add((nhm_uri, RDF.type, ORG.Organization))
        g.add((nhm_uri, RDF.type, FOAF.Organization))
        # Update the name
        g.set((nhm_uri, FOAF.name, Literal('Natural History Museum')))

        # # Add TDWG institution details - http://rs.tdwg.org/ontology/voc/Institution
        g.set((nhm_uri, TDWGI.acronymOrCoden, Literal('NHMUK')))
        g.set((nhm_uri, TDWGI.institutionType, URIRef('http://rs.tdwg.org/ontology/voc/InstitutionType#museum')))
        # Add AIISO institution
        g.add((nhm_uri, RDF.type, AIISO.Institution))
        # Add same as link
        g.add((nhm_uri, OWL.sameAs, URIRef('http://dbpedia.org/resource/Natural_history_museum')))
        g.add((nhm_uri, OWL.sameAs, URIRef('https://www.wikidata.org/wiki/Q309388')))

        if user:
            user_uri = URIRef(self.user_uri(creator_user_id))
            g.add((user_uri, RDF.type, VCARD.Person))
            g.add((user_uri, VCARD.fn, Literal(user['fullname'])))
            g.add((user_uri, VCARD.hasEmail, URIRef(user['email'])))
            # All users are members of the NHM
            g.add((user_uri, MADS.hasAffiliation, nhm_uri))

            # This user is the contact point for the dataset
            g.add((dataset_uri, DCAT.contactPoint, user_uri))

        # Add update frequency
        update_frequency = dataset_dict.get('update_frequency', None)
        if update_frequency:
            code = self._get_update_frequency_code(update_frequency)
            if code:
                g.set((dataset_uri, DCT.accrualPeriodicity, URIRef(SDMX_CODE[code])))

        # Add licence - use URL if we have it
        # Otherwise try using the licence title
        if dataset_dict.get('license_url', None):
            g.set((dataset_uri, DCT.license, URIRef(dataset_dict['license_url'])))
        elif dataset_dict.get('license_title', None):
            g.set((dataset_uri, DCT.license, Literal(dataset_dict['license_title'])))

        # Add categories
        # Create concept schema for all categories, add link any related to the dataset
        for category in dataset_dict['dataset_category']:
            # print category
            n = BNode()
            g.add((n, rdflib.RDF.type, SKOS.Concept))
            g.add((n, SKOS.prefLabel, Literal(category)))
            g.add((dataset_uri, DCAT.theme, n))

        # Temporal extent
        temporal_extent = dataset_dict.get('temporal_extent', None)
        if temporal_extent:
            g.add((dataset_uri, DCT.temporal, Literal(temporal_extent)))

        author = dataset_dict.get('author', None)
        if author:

            if author == 'Natural History Museum':
                g.add((dataset_uri, DCT.creator, nhm_uri))
            else:
                author_details = BNode()
                g.add((author_details, VCARD.fn, Literal(author)))
                if dataset_dict.get('author_email', None):
                    g.add((author_details, VCARD.hasEmail, Literal(dataset_dict['author_email'])))
                g.add((author_details, RDF.type, VCARD.Person))
                g.add((dataset_uri, DCT.creator, author_details))
                affiliation = dataset_dict.get('affiliation', None)
                if affiliation:
                    if affiliation == 'Natural History Museum':
                        g.add((author_details, MADS.hasAffiliation, nhm_uri))
                    else:
                        g.add((author_details, MADS.hasAffiliation, Literal(affiliation)))

        contributors = dataset_dict.get('contributors', None)
        if contributors:
            g.add((dataset_uri, DCT.contributor, Literal(contributors)))

        self.graph_add_resources(dataset_uri, dataset_dict)

    def graph_from_record(self, dataset_dict, dataset_ref):

        pass

