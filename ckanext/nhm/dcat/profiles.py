
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import os
import rdflib
import json
from rdflib.namespace import Namespace, RDF, XSD, RDFS
from rdflib import URIRef, BNode, Literal
from rdflib import OWL
from rdflib.namespace import FOAF, SKOS
from dateutil.parser import parse as parse_date
from pylons import request

from ckan.plugins import toolkit
from ckan.lib.helpers import url_for
import ckan.lib.base as base
import ckan.logic as logic

from ckanext.dcat.utils import resource_uri, dataset_uri, catalog_uri
from ckanext.dcat.profiles import RDFProfile

from ckanext.nhm.lib.dwc import dwc_terms
from ckanext.nhm.lib.helpers import get_department
from ckanext.nhm.dcat.utils import rdf_resources

abort = base.abort
NotFound = logic.NotFound

DC = Namespace(u'http://purl.org/dc/terms/')
DCAT = Namespace(u'http://www.w3.org/ns/dcat#')
ADMS = Namespace(u'http://www.w3.org/ns/adms#')
VCARD = Namespace(u'http://www.w3.org/2006/vcard/ns#')
FOAF = Namespace(u'http://xmlns.com/foaf/0.1/')
SCHEMA = Namespace(u'http://schema.org/')
TIME = Namespace(u'http://www.w3.org/2006/time')
LOCN = Namespace(u'http://www.w3.org/ns/locn#')
GSP = Namespace(u'http://www.opengis.net/ont/geosparql#')
OWL = Namespace(u'http://www.w3.org/2002/07/owl#')
SDMX_CODE = Namespace(u'http://purl.org/linked-data/sdmx/2009/code#')
TDWGI = Namespace(u'http://rs.tdwg.org/ontology/voc/Institution#')
AIISO = Namespace(u'http://purl.org/vocab/aiiso/schema#')
MADS = Namespace(u'http://www.loc.gov/mads/rdf/v1#')
VOID = Namespace(u'http://rdfs.org/ns/void#')
CC = Namespace(u'http://creativecommons.org/ns#')
ORG = Namespace(u'http://www.w3.org/TR/vocab-org/#')
DWC = Namespace(u'http://rs.tdwg.org/dwc/terms/')
SDWC = Namespace(u'http://rs.tdwg.org/dwc/xsd/simpledarwincore#')
DQV = Namespace(u'http://www.w3.org/ns/dqv#')

METADATA_LICENCE = u'http://creativecommons.org/publicdomain/zero/1.0/'

class NHMDCATProfile(RDFProfile):
    '''An RDF profile for the NHM
    
    http://www.w3.org/2011/gld/wiki/Data_Catalog_Vocabulary/Recipes
    http://rdf-vocabulary.ddialliance.org/discovery.html


    '''

    def _get_update_frequency_code(self, frequency):
        '''

        :param frequency: 

        '''
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
        '''

        :param id: 

        '''
        return u'{0}/user/{1}'.format(catalog_uri().rstrip('/'), id)

    def get_context(self):
        '''Set up context
        :return: context dict


        '''
        user = toolkit.get_action(u'get_site_user')({u'ignore_auth': True}, {})
        context = {u'user': user[u'name']}
        return context

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        '''

        :param dataset_dict: 
        :param dataset_ref: 

        '''

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
        if dataset_dict[u'name'] in request.environ.get(u'CKAN_CURRENT_URL'):
            alt_dataset_uri = u'{0}/dataset/{1}'.format(catalog_uri().rstrip('/'), dataset_dict[u'name'])
            # Add a sameAs link
            g.add((dataset_metadata_uri, OWL.sameAs, URIRef(alt_dataset_uri)))
        # And now we can describe the dataset itself
        g.add((dataset_uri, RDF.type, DCAT.Dataset))

        # Basic fields
        items = [
            (u'title', DC.title, None),
            (u'url', DCAT.landingPage, None),
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
            (u'issued', DC.issued, [u'metadata_created']),
            (u'modified', DC.modified, [u'metadata_modified']),
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
            full_name = user.get(u'fullname', None)
            # If this is the Natural History Museum user (i.e. admin), just add the contactPoint
            if full_name == u'Natural History Museum':
                g.add((dataset_uri, DCAT.contactPoint, nhm_uri))
            else:
                user_uri = URIRef(self.user_uri(creator_user_id))
                g.add((user_uri, RDF.type, VCARD.Person))
                g.add((user_uri, VCARD.fn, Literal(full_name)))
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
        ''' '''

        g = self.g
        nhm_uri = URIRef(u'http://nhm.ac.uk')
        g.add((nhm_uri, RDF.type, ORG.Organization))
        g.add((nhm_uri, RDF.type, FOAF.Organization))
        # Update the name
        g.set((nhm_uri, FOAF.name, Literal(u'Natural History Museum')))
        # # Add TDWG institution details - http://rs.tdwg.org/ontology/voc/Institution
        g.set((nhm_uri, TDWGI.acronymOrCoden, Literal(u'NHMUK')))
        g.set((nhm_uri, TDWGI.institutionType, URIRef(u'http://rs.tdwg.org/ontology/voc/InstitutionType#museum')))
        # Add AIISO institution
        g.add((nhm_uri, RDF.type, AIISO.Institution))
        # Add same as link
        g.add((nhm_uri, OWL.sameAs, URIRef(u'http://dbpedia.org/resource/Natural_history_museum')))
        g.add((nhm_uri, OWL.sameAs, URIRef(u'https://www.wikidata.org/wiki/Q309388')))
        return nhm_uri


    def graph_add_resources(self, dataset_uri, dataset_dict):
        '''

        :param dataset_uri: 
        :param dataset_dict: 

        '''

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
                (u'name', DC.title, None),
                (u'description', DC.description, None),
                (u'status', ADMS.status, None),
                (u'rights', DC.rights, None),
                (u'license', DC.license, None),
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
                (u'issued', DC.issued, None),
                (u'modified', DC.modified, None),
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

    def graph_from_record(self, record_dict, resource, record_ref):
        '''RDF for an individual record - currently this is a specimen record
        
        Similar approach to: curl -L -H "Accept: application/rdf+ttl" http://data.rbge.org.uk/herb/E00321910

        :param record_dict: param resource:
        :param record_ref: return:
        :param resource: 

        '''
        context = self.get_context()
        namespaces = {
            u'dc': DC,
            u'dcat': DCAT,
            u'dwc': DWC,
            u'sdwc': SDWC,
            u'void': VOID,
            u'cc': CC,
            u'foaf': FOAF,
            u'dqv': DQV,
            u'aiiso': AIISO,
            u'tdwgi': TDWGI,
            u'owl': OWL
        }

        g = self.g

        # Add some more namespaces
        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        # Get the GBIF record if it exists
        occurrence_id = record_dict.get(u'occurrenceID')

        package_id = resource.get_package_id()

        # Create licences metadata for record
        object_uri = URIRef(record_ref + u'#object')

        # Add publisher - as per BBC we don't need the full org description here
        nhm_uri = URIRef(u'http://nhm.ac.uk')

        # Add object description - the metadata and license
        g.add((record_ref, RDF.type, FOAF.Document))
        g.add((record_ref, CC.license, URIRef(METADATA_LICENCE)))
        # This metadata describes #dataset
        g.add((record_ref, FOAF.primaryTopic, object_uri))
        # Add the de-referenced link to record
        record_link = url_for(u'record', action=u'view', package_name=package_id, resource_id=resource.id, record_id=record_dict[u'_id'], qualified=True)
        g.add((record_ref, DC.hasVersion, URIRef(record_link)))
        # Add institution properties
        g.add((record_ref, FOAF.organization, nhm_uri))
        g.add((record_ref, AIISO.Department, Literal(get_department(record_dict[u'collectionCode']))))

        try:
            sub_dept = record_dict.pop(u'subDepartment')
        except KeyError:
            pass
        else:
            g.add((record_ref, AIISO.Division, Literal(sub_dept)))

        # Created and modified belong to the metadata record, not the specimen
        for term in [u'created', u'modified']:
            try:
                value = record_dict.get(term)
            except KeyError:
                pass
            else:
                # Parse into data format, and add as dates
                _date = parse_date(value)
                g.add((record_ref, getattr(DWC, term), Literal(_date.isoformat(), datatype=XSD.dateTime)))

        try:
            gbif_record = toolkit.get_action(u'gbif_record_show')(context, {
                u'occurrence_id': occurrence_id
            })
        except NotFound:
            gbif_record = {}
        else:
            # Assert equivalence with the GBIF record
            gbif_uri = os.path.join(u'http://www.gbif.org/occurrence', gbif_record[u'gbifID'])
            g.add((object_uri, OWL.sameAs, URIRef(gbif_uri)))
            # If we have a GBIF country code, add it
            # Annoyingly, this seems to be the only geographic element on GBIF with URI
            country_code = gbif_record.get(u'gbifCountryCode')
            if country_code:
                g.add((object_uri, DWC.countryCode, URIRef(os.path.join(u'http://www.gbif.org/country', country_code))))

        # Now, create the specimen object
        # Remove nulls and hidden fields from record_dict
        record_dict = dict((k, v) for k, v in record_dict.iteritems() if v)

        # Now add the actual specimen object
        g.add((object_uri, RDF.type, FOAF.Document))
        g.add((object_uri, RDF.type, SDWC.SimpleDarwinRecordSet))

        # Make sure decimal latitude and longitude are strings
        for d in [u'decimalLatitude', u'decimalLongitude']:
            try:
                record_dict[d] = str(record_dict[d])
            except KeyError:
                pass

        # Adding images as JSON is rubbish! So lets try and do it properly
        try:
            associated_media = record_dict.pop(u'associatedMedia')
        except KeyError:
            pass
        else:
            images = json.loads(associated_media)
            for image in images:
                image_uri = URIRef(image[u'identifier'])
                g.set((image_uri, RDF.type, FOAF.Image))
                title = image.get(u'title', None)
                if title:
                    g.set((image_uri, DC.title, Literal(title)))
                g.set((image_uri, CC.license, URIRef(image[u'license'])))
                g.set((image_uri, DC.RightsStatement, Literal(image[u'rightsHolder'])))
                g.set((image_uri, DC.Format, Literal(image[u'format'])))
                # Add link from image to object...
                g.set((image_uri, FOAF.depicts, object_uri))
                # And object to image
                g.add((object_uri, FOAF.depiction, image_uri))

        # This record belongs in X dataset
        dataset_ref = URIRef(dataset_uri({u'id': package_id}) + u'#dataset')
        g.add((object_uri, VOID.inDataset, dataset_ref))

        dwc_terms_dict = dwc_terms(record_dict.keys())

        # Handle dynamic properties separately
        dynamic_properties = dwc_terms_dict.pop(u'dynamicProperties')

        for group, terms in dwc_terms_dict.items():
            for uri, term in terms.items():
                # Do we have a GBIF key value?
                # Uppercase first letter of term, and convert to GBIF key format => gbifGenusKey
                uc_term = term[0].upper() + term[1:]
                gbif_term_key = u'gbif%sKey' % uc_term
                gbif_key = gbif_record.get(gbif_term_key)

                # Do we have a GBIF key value? If we do, we can provide a URI to GBIF
                if gbif_key:
                    gbif_uri = URIRef(os.path.join(u'http://www.gbif.org/species', gbif_key))
                    # Add the GBIF species URI with label
                    g.add((gbif_uri, RDFS.label, Literal(record_dict.get(term))))
                    # And associated our specimen object's DWC term with the GBIF URI
                    g.add((object_uri, getattr(DWC, term), gbif_uri))
                else:
                    # We do not have a GBIF key, so no URI: Add the term value as a literal
                    g.add((object_uri, getattr(DWC, term), Literal(record_dict.get(term))))

        g.add((object_uri, DC.identifier, Literal(record_dict.get(u'uuid'))))

        dynamic_properties_dict = {}
        for properties in dynamic_properties.values():
            for property in properties:
                dynamic_properties_dict[property] = record_dict.get(property)
        if dynamic_properties_dict:
            g.add((object_uri, DWC.dynamicProperties, Literal(json.dumps(dynamic_properties_dict))))

        # try:
        #     dqi = record_dict.pop('dqi')
        # except KeyError:
        #     pass
        # else:
        #     pass
        #     # TODO: Add DQV. Currently there are none in use
        #     # if dqi != 'Unknown':
        #     #     n = BNode()
