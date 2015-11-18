
import rdflib
from pylons import config
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib import URIRef, BNode, Literal
from ckanext.dcat.utils import resource_uri, publisher_uri_from_dataset_dict, dataset_uri
from ckanext.dcat.profiles import RDFProfile
from ckan.lib.helpers import url_for
from rdflib import OWL
from rdflib.namespace import FOAF, SKOS
from ckanext.nhm.lib.helpers import dataset_categories

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SDMX_CODE = Namespace("http://purl.org/linked-data/sdmx/code#")
TDWGI = Namespace('http://rs.tdwg.org/ontology/voc/Institution#')
AIISO = Namespace('http://purl.org/vocab/aiiso/schema#')
MADS = Namespace('http://www.loc.gov/mads/rdf/v1#')
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

namespaces = {
    'tdwgi': TDWGI,
    'aiiso': AIISO,
    'mads': MADS
}

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

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Add some more namespaces
        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        dataset = URIRef(dataset_ref)
        self._update_publisher(g)

        # Add update frequency
        update_frequency = dataset_dict.get('update_frequency', None)
        if update_frequency:
            code = self._get_update_frequency_code(update_frequency)
            if code:
                g.set((dataset, DCT.accrualPeriodicity, URIRef(SDMX_CODE[code])))

        # Add licence
        license = dataset_dict.get('license_url', None)
        if license:
            g.set((dataset, DCT.license, URIRef(license)))

        doi = dataset_dict.get('doi', None)
        if doi:
            g.set((dataset, DCT.identifier, URIRef(doi)))

        for resource_dict in dataset_dict.get('resources', []):
            resource_uri_ref = URIRef(resource_uri(resource_dict))
            # As we don't allow direct download of the data, we need to add landing page
            # To dataset - see http://www.w3.org/TR/vocab-dcat/#example-landing-page
            g.add((dataset, DCAT.landingPage, resource_uri_ref))
            # Update the accessURL for the resource distribution
            g.set((resource_uri_ref, DCAT.accessURL, resource_uri_ref))

        # Add categories
        # Create concept schema for all categories, add link any related to the dataset
        for category in dataset_dict['dataset_category']:
            # print category
            n = BNode()
            g.add((n, rdflib.RDF.type, SKOS.Concept))
            g.add((n, SKOS.prefLabel, Literal(category)))
            g.add((dataset, DCAT.theme, n))

        # Temporal extent
        temporal_extent = dataset_dict.get('temporal_extent', None)
        if temporal_extent:
            g.add((dataset, DCT.temporal, Literal(temporal_extent)))

        author = dataset_dict.get('author', None)
        if author:
            contact_uri = self._get_dataset_value(dataset_dict, 'contact_uri')
            if contact_uri:
                contact_details = URIRef(contact_uri)
            else:
                contact_details = BNode()

            items = [
                ('contact_name', VCARD.fn, ['maintainer', 'author']),
                ('contact_email', VCARD.hasEmail, ['maintainer_email',
                                                   'author_email']),
            ]

            self._add_triples_from_dict(dataset_dict, contact_details, items)

            g.add((contact_details, RDF.type, VCARD.Person))
            g.add((dataset_ref, DCT.creator, contact_details))

            affiliation = dataset_dict.get('affiliation', None)
            if affiliation:
                g.add((contact_details, MADS.hasAffiliation, Literal(affiliation)))

        contributors = dataset_dict.get('contributors', None)
        if contributors:
            g.add((dataset_ref, DCT.contributor, Literal(contributors)))

        # Update contact point to type is person, not organisation
        contact_point = g.value(subject=dataset, predicate=DCAT.contactPoint)
        g.set((contact_point, RDF.type, VCARD.Person))
