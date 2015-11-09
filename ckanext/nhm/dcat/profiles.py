import rdflib
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib import URIRef, BNode, Literal

from ckanext.dcat.profiles import RDFProfile


DCT = Namespace("http://purl.org/dc/terms/")
SDMX_CODE = Namespace("http://purl.org/linked-data/sdmx/code#")


class NHMDCATProfile(RDFProfile):
    '''
    An RDF profile for the Swedish DCAT-AP recommendation for data portals
    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Spatial label
        spatial = self._object(dataset_ref, DCT.spatial)
        if spatial:
            spatial_label = self.g.label(spatial)
            if spatial_label:
                dataset_dict['extras'].append({'key': 'spatial_text',
                                               'value': str(spatial_label)})

        return dataset_dict


    # def graph_from_catalog(self, catalog_dict, catalog_ref):

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Add update frequency = DCAT::accrualPeriodicity
        update_frequency = dataset_dict.get('update_frequency', None)
        if update_frequency:
        #     print SDMX.freq
        #
        #
        # print rdflib.term.URIRef('http://www.w3.org/2002/07/owl#seeAlso')

            print URIRef(SDMX_CODE + "status-M")


        # print dataset_dict

        # spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
        # spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')
        #
        # spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')
        #
        # if spatial_uri:
        #     spatial_ref = URIRef(spatial_uri)
        # else:
        #     spatial_ref = BNode()
        #
        # g.add((spatial_ref, RDF.type, DCT.Location))
        # g.add((dataset_ref, DCT.spatial, spatial_ref))
        #
        # if spatial_text:
        #     g.add((spatial_ref, RDFS.label, Literal(spatial_text)))