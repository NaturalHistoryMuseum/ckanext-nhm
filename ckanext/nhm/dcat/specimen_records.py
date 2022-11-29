#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from typing import Optional

import itertools
import json
from ckan.plugins import toolkit
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.utils import url_to_rdflib_format, dataset_uri
from ckanext.nhm.dcat.utils import (
    Namespaces,
    object_uri,
    as_dwc_list,
    epoch_to_datetime,
)
from ckanext.nhm.lib.dwc import dwc_terms
from ckanext.nhm.lib.helpers import get_department
from ckanext.nhm.lib.record import Record
from datetime import datetime
from rdflib import URIRef, Literal


class ObjectSerializer(RDFSerializer):
    """
    Simple subclass of the RDFSerializer class that just simply adds a record serializer
    method.
    """

    serializer_kwargs = {
        'json-ld': {
            # this compacts the json output so that the namespaces are declared at the start in a
            # @context field rather than when each value is included
            'auto_compact': True
        },
        'pretty-xml': {
            # this prevents the serializer nesting resource tags inside each other thus forcing the
            # metadata, data and any image tags to appear individually
            'max_depth': 1
        },
    }

    def serialize_record(
        self, record: Record, output_format: str = 'xml', version: Optional[int] = None
    ):
        """
        Given a record dict, returns an RDF serialization.

        The serialization format can be defined using the `_format` parameter. It must be one of the
        ones supported by RDFLib, defaults to `xml`.

        Returns a string with the serialized dataset
        """
        rdflib_format = url_to_rdflib_format(output_format)
        builder = RecordGraphBuilder(record, Namespaces(self.g), output_format, version)

        for triple in builder:
            # the builder is allowed to yield duplicate triples so using add here just defers the
            # handling of these to the triplestore itself, which it handles fine. We could use set
            # to be more proactive with de-duplication, however the replace part of the set function
            # removes all previously added subject-predicate pairs and is therefore too aggressive
            # (i.e. set(x, y, a) followed by set(x, y, b) would result in (x, y, b) in the
            # triplestore and the (x, y, a) triple would be removed)
            self.g.add(triple)

        return self.g.serialize(
            format=rdflib_format, **self.serializer_kwargs.get(rdflib_format, {})
        )


class RecordGraphBuilder(object):
    """
    Class that can generate the triples necessary to represent a record in rdf format.
    """

    def __init__(
        self,
        record: Record,
        namespaces: Namespaces,
        output_format: str,
        version: Optional[int],
    ):
        '''
        :param record: a Record object
        :param namespaces: the namespaces object to use
        :param output_format: the format the generated graph will be output in. This will be used to
                              create the metadata URI (i.e. object_url + .{output_format})
        :param version: the version of the record in question, or None if there is no version
        '''
        self.record = record
        self.namespaces = namespaces
        self.output_format = output_format
        self.version = version

        # figure out the rounded version of the record
        self.rounded_version = toolkit.get_action('datastore_get_rounded_version')(
            {},
            {
                'resource_id': self.record.resource_id,
                'version': self.version,
            },
        )

        # figure out the object URI for the record (possibly with version)
        if version is None:
            self.base_object_uri = object_uri(record.data['occurrenceID'])
        else:
            self.base_object_uri = object_uri(
                record.data['occurrenceID'], version=self.rounded_version
            )
        # this will be used as the subject for any record data triples
        self.record_ref = URIRef(self.base_object_uri)

        # grab the gbif version of the record if we can
        self.gbif_record = self._get_gbif_record()

    def _get_gbif_record(self):
        """
        Retrieve the GBIF representation of the record if we can.

        :return: the GBIF record dict or None if we couldn't get it or didn't have a GBIF ID
                 associated with the record
        """
        gbif_id = self.record.data.get('gbifID', None)

        if gbif_id is not None:
            try:
                context = {'ignore_auth': True}
                data_dict = {'gbif_id': gbif_id}
                return toolkit.get_action('gbif_record_show')(context, data_dict)
            except toolkit.ObjectNotFound:
                pass
        return None

    def __iter__(self):
        """
        Iterating over this object will yield the triples that represent the record.

        :return: yields 3-tuples
        """
        triple_generators = [
            self._metadata(),
            self._cetaf_cspp(),
            self._gbif(),
            self._images(),
            self._dwc(),
            self._version_info(),
            self._extras(),
        ]

        for triple in itertools.chain(*triple_generators):
            # if the object part of the triple is None, don't yield it. This is tied to the
            # _get_value function on this class which essentially provides a way of avoiding having
            # to use lots of if checks (i.e. if field has value, yield)
            if triple[2] is not None:
                yield triple

    def _get_value(self, field, source=None):
        """
        Retrieve a value from the given source and yield it wrapped in a Literal. The
        default source is the self.record.data dict. This function works in conjunction
        with the __iter__ function above which filters out triples containing a None as
        the object (the 3rd value).

        :param field: the field to get the value of
        :param source: the source dict to retrieve the field's value from
        :return: the value wrapped in a Literal or None if the field doesn't exist on the source
        """
        if source is None:
            source = self.record.data
        value = source.get(field, None)
        if value is not None:
            return Literal(value)
        else:
            return None

    def _metadata(self):
        """
        Yields triples which describe this RDF output, i.e. a meta-metadata description.

        :return: yields triples
        """
        metadata_uri = '{}.{}'.format(self.base_object_uri, self.output_format)
        meta_ref = URIRef(metadata_uri)
        yield meta_ref, self.namespaces.dc.subject, self.record_ref
        yield meta_ref, self.namespaces.dc.creator, Literal(
            'Natural History Museum, London'
        )
        yield meta_ref, self.namespaces.dc.created, Literal(datetime.now())

    def _cetaf_cspp(self):
        """
        Yields the triples required for the record data to ensure we conform to the
        CETAF CSPP recommendations, for more info see here:
        https://cetafidentifiers.biowikifarm.net/wiki/CSPP.

        :return: yields triples
        """
        yield self.record_ref, self.namespaces.dc.title, self._get_value(
            'scientificName'
        )
        yield self.record_ref, self.namespaces.dc.type, Literal('Specimen')
        yield (
            self.record_ref,
            self.namespaces.dwc.scientificName,
            self._get_value('scientificName'),
        )
        yield self.record_ref, self.namespaces.dwc.family, self._get_value('family')

        # find the previous determinations for this record and yield them as the
        # previousIdentifications term, ignoring the current determination the record is filed as
        determination_names = self.record.data.get('determinationNames', [])
        filed_as = self.record.data.get('determinationFiledAs', [])
        if determination_names and filed_as:
            names = (
                name
                for name, filed in zip(determination_names, filed_as)
                if filed == 'No'
            )
            yield (
                self.record_ref,
                self.namespaces.dwc.previousIdentifications,
                Literal(as_dwc_list(names)),
            )

        yield self.record_ref, self.namespaces.dwc.fieldNumber, self._get_value(
            'fieldNumber'
        )
        yield self.record_ref, self.namespaces.dwc.recordedBy, self._get_value(
            'recordedBy'
        )

        # if there is associated media, yield it as a list
        images = self.record.images
        if images:
            value = as_dwc_list(image.url for image in images)
            yield self.record_ref, self.namespaces.dwc.associatedMedia, Literal(value)

        yield (
            self.record_ref,
            self.namespaces.dwc.decimalLatitude,
            self._get_value('decimalLatitude'),
        )
        yield (
            self.record_ref,
            self.namespaces.dwc.decimalLongitude,
            self._get_value('decimalLongitude'),
        )

        # if there's a GBIF record, see if we can yield a country code for the record from it
        if self.gbif_record is not None:
            yield (
                self.record_ref,
                self.namespaces.dwc.countryCode,
                self._get_value('countryCode', source=self.gbif_record),
            )

        if self.record.data.get('created', None) is not None:
            yield (
                self.record_ref,
                self.namespaces.dc.created,
                Literal(epoch_to_datetime(self.record.data['created'])),
            )
        yield self.record_ref, self.namespaces.dc.publisher, URIRef('https://nhm.ac.uk')

    def _images(self):
        """
        Yields triples describing the images associated with this record, if there are
        any. Each image is connected to the record through a FOAF depicts field
        connection and then the image is described in its own set of triples where the
        image URI is used as the subject.

        :return: yields triples
        """
        for image in self.record.images:
            image_uri = URIRef(image.url)
            yield image_uri, self.namespaces.rdf.type, self.namespaces.foaf.Image

            yield image_uri, self.namespaces.dc.title, Literal(image.title)
            yield image_uri, self.namespaces.cc.license, URIRef(image.license_url)
            yield image_uri, self.namespaces.dc.RightsStatement, Literal(image.rights)
            # although the actual image could be something else, the preview will always be a jpeg
            yield image_uri, self.namespaces.dc.format, Literal('image/jpeg')
            # add link from image to object
            yield image_uri, self.namespaces.foaf.depicts, self.record_ref
            # add a link from the object to the image
            yield self.record_ref, self.namespaces.foaf.depiction, image_uri
            # add a thumbnail link
            if image.is_mss_image:
                yield image_uri, self.namespaces.foaf.thumbnail, URIRef(
                    image.thumbnail_url
                )

    def _gbif(self):
        """
        Yields triples describing the record using the GBIF record data associated with
        it.

        :return: yields triples
        """
        if self.gbif_record is not None:
            # assert equivalence with the GBIF record
            yield self.record_ref, self.namespaces.owl.sameAs, URIRef(
                'https://www.gbif.org/occurrence/{}'.format(self.gbif_record['gbifID'])
            )
            # if we have a GBIF country code, add it
            yield (
                self.record_ref,
                self.namespaces.dwc.countryCode,
                self._get_value('countryCode', source=self.gbif_record),
            )

    def _dwc(self):
        """
        Yields triples describing the record using DWC (DarWin Core) terms.

        :return: yields triples
        """
        yield self.record_ref, self.namespaces.dc.identifier, Literal(
            self.record.data['occurrenceID']
        )

        dwc_terms_dict = dwc_terms(self.record.data.keys())

        groups_to_skip = {'dynamicProperties'}
        terms_to_skip = {'associatedMedia', 'created', 'modified'}
        for group, terms in dwc_terms_dict.items():
            if group in groups_to_skip:
                continue

            for uri, term in terms.items():
                if term in terms_to_skip:
                    continue

                if self.gbif_record is not None:
                    gbif_key = self.gbif_record.get(f'{term}Key')
                    if gbif_key:
                        gbif_uri = URIRef(f'http://www.gbif.org/species/{gbif_key}')
                        # add the GBIF species URI with label
                        yield (
                            gbif_uri,
                            self.namespaces.rdfs.label,
                            Literal(self.record.data.get(term)),
                        )
                        # and associated our specimen object's DWC term with the GBIF URI
                        yield self.record_ref, getattr(
                            self.namespaces.dwc, term
                        ), gbif_uri
                else:
                    yield (
                        self.record_ref,
                        getattr(self.namespaces.dwc, term),
                        Literal(self.record.data.get(term)),
                    )

        # retrieve the dynamic properties and yield them as one JSON dump
        dynamic_properties_dict = {}
        for properties in dwc_terms_dict.get('dynamicProperties', {}).values():
            for dynamic_property in properties:
                if dynamic_property == 'created':
                    continue
                dynamic_properties_dict[dynamic_property] = self.record.data.get(
                    dynamic_property
                )
        if dynamic_properties_dict:
            yield self.record_ref, self.namespaces.dwc.dynamicProperties, Literal(
                json.dumps(dynamic_properties_dict)
            )

        # yield the associatedMedia term as a pipe-separated list of image URIs
        images = self.record.images
        if images:
            yield self.record_ref, self.namespaces.dwc.associatedMedia, Literal(
                as_dwc_list(image.url for image in images)
            )

        if self.record.data.get('created', None) is not None:
            # yield the created date in the correct format
            yield (
                self.record_ref,
                self.namespaces.dc.created,
                Literal(epoch_to_datetime(self.record.data['created'])),
            )

        if self.record.data.get('modified', None) is not None:
            # yield the modified date in the correct format
            yield (
                self.record_ref,
                self.namespaces.dwc.modified,
                Literal(epoch_to_datetime(self.record.data['modified'])),
            )

    def _version_info(self):
        """
        Yield simple version information about the record.

        :return: yields triples
        """
        yield self.record_ref, self.namespaces.owl.versionInfo, Literal(
            self.rounded_version
        )

        if self.version is None or self.version > self.rounded_version:
            # if there is no version given or the version requested is beyond the latest version the
            # data we're using is the same as the latest version's data, yield a same as to show
            # this
            yield self.record_ref, self.namespaces.owl.sameAs, URIRef(
                object_uri(
                    self.record.data['occurrenceID'], version=self.rounded_version
                )
            )

    def _extras(self):
        """
        Yields some additional triples that don't really fit under any of the other
        existing method groupings.

        :return: yields triples
        """
        yield (
            self.record_ref,
            self.namespaces.aiiso.Department,
            Literal(get_department(self.record.data['collectionCode'])),
        )
        yield self.record_ref, self.namespaces.aiiso.Division, self._get_value(
            'subDepartment'
        )

        yield (
            self.record_ref,
            self.namespaces.void.inDataset,
            URIRef(dataset_uri({'id': self.record.package_id}) + '#dataset'),
        )
