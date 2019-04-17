#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from collections import OrderedDict
from copy import deepcopy

import re
from ckanext.nhm.lib.filter_options import exclude_mineralogy, has_image, has_lat_long
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.views.dwc import DarwinCoreView

from ckan.plugins import toolkit

log = logging.getLogger(__name__)


class SpecimenView(DefaultView):
    '''Controller for displaying a specimen record'''
    resource_id = toolkit.config.get(u'ckanext.nhm.specimen_resource_id')

    grid_default_columns = DarwinCoreView.grid_default_columns
    grid_column_widths = DarwinCoreView.grid_column_widths

    field_facets = [
        'collectionCode',
        'typeStatus',
        'family',
        'genus',
        'associatedMedia.category',
        'gbifIssue'
        ]

    # Additional search filter options
    filter_options = [has_image, has_lat_long, exclude_mineralogy]

    field_groups = OrderedDict([
        (u'Classification', OrderedDict([
            (u'scientificName', u'Scientific name'),
            (u'scientificNameAuthorship', u'Author'),
            (u'kingdom', u'Kingdom'),
            (u'phylum', u'Phylum'),
            (u'class', u'Class'),
            (u'order', u'Order'),
            (u'family', u'Family'),
            (u'genus', u'Genus'),
            (u'subgenus', u'Subgenus'),
            (u'specificEpithet', u'Species'),
            (u'infraspecificEpithet', u'Subspecies'),
            (u'higherClassification', u'Higher classification'),
            (u'taxonRank', u'Taxon rank'),
            ])),
        (u'Location', OrderedDict([
            (u'labelLocality', u'Label locality'),
            (u'locality', u'Locality'),
            (u'stateProvince', u'State province'),
            (u'mine', u'Mine'),
            (u'miningDistrict', u'Mining district'),
            (u'viceCounty', u'Vice County'),
            (u'country', u'Country'),
            (u'continent', u'Continent'),
            (u'island', u'Island'),
            (u'islandGroup', u'Island group'),
            (u'waterBody', u'Water body'),
            (u'higherGeography', u'Higher geography'),
            (u'decimalLatitude', u'Decimal latitude'),
            (u'decimalLongitude', u'Decimal longitude'),
            (u'verbatimLatitude', u'Verbatim latitude'),
            (u'verbatimLongitude', u'Verbatim longitude'),
            (u'centroid', u'Centroid'),
            (u'maxError', u'Max error'),
            (u'geodeticDatum', u'Geodetic datum'),
            (u'georeferenceProtocol', u'Georeference protocol'),
            (u'minimumElevationInMeters', u'Minimum elevation(m)'),
            (u'maximumElevationInMeters', u'Maximum elevation(m)'),
            (u'minimumDepthInMeters', u'Minimum depth(m)'),
            (u'maximumDepthInMeters', u'Maximum depth(m)'),
            ])),
        (u'Collection event', OrderedDict([
            (u'recordedBy', u'Recorded by'),
            (u'recordNumber', u'Record number'),
            (u'year', u'Year'),
            (u'month', u'Month'),
            (u'day', u'Day'),
            (u'eventTime', u'Event time'),
            (u'expedition', u'Expedition'),
            (u'habitat', u'Habitat'),
            (u'vessel', u'Vessel'),
            (u'samplingProtocol', u'Sampling protocol'),
            ])),
        (u'Identification', OrderedDict([
            (u'identifiedBy', u'Identified by'),
            (u'dateIdentified', u'Date identified'),
            (u'identificationQualifier', u'Identification qualifier'),
            (u'typeStatus', u'Type status'),
            (u'determinations', u'Determinations'),
            ])),
        (u'Specimen', OrderedDict([
            (u'catalogNumber', u'Catalogue number'),
            (u'collectionCode', u'Collection code'),
            (u'subDepartment', u'Sub department'),
            (u'otherCatalogNumbers', u'Other catalog numbers'),
            (u'registrationCode', u'Registration code'),
            (u'kindOfObject', u'Kind of object'),
            (u'preparations', u'Preparations'),
            (u'preparationType', u'Preparation type'),
            (u'preservative', u'Preservative'),
            (u'collectionKind', u'Collection kind'),
            (u'collectionName', u'Collection name'),
            (u'donorName', u'Donor name'),
            (u'kindOfCollection', u'Kind of collection'),
            (u'observedWeight', u'Observed weight'),
            (u'individualCount', u'Individual count'),
            (u'sex', u'Sex'),
            (u'lifeStage', u'Life stage'),
            (u'catalogueDescription', u'Catalogue description'),
            ])),
        (u'Mineralogy', OrderedDict([
            (u'dateRegistered', u'Date registered'),
            (u'occurrence', u'Occurrence'),
            (u'commodity', u'Commodity'),
            (u'depositType', u'Deposit type'),
            (u'texture', u'Texture'),
            (u'identificationAsRegistered', u'Identification as registered'),
            (u'identificationDescription', u'Identification description'),
            (u'identificationVariety', u'Identification variety'),
            (u'identificationOther', u'Identification other'),
            (u'hostRock', u'Host rock'),
            (u'age', u'Age'),
            (u'ageType', u'Age type'),
            (u'geologyRegion', u'Geology region'),
            (u'mineralComplex', u'Mineral complex'),
            (u'tectonicProvince', u'Tectonic province'),
            (u'registeredWeight', u'Registered weight'),
            ])),
        (u'Stratigraphy', OrderedDict([
            (u'earliestEonOrLowestEonothem', u'Earliest eon/lowest eonothem'),
            (u'latestEonOrHighestEonothem', u'Latest eon/highest eonothem'),
            (u'earliestEraOrLowestErathem', u'Earliest era/lowest erathem'),
            (u'latestEraOrHighestErathem', u'Latest era/highest erathem'),
            (u'earliestPeriodOrLowestSystem', u'Earliest period/lowest system'),
            (u'latestPeriodOrHighestSystem', u'Latest period/highest system'),
            (u'earliestEpochOrLowestSeries', u'Earliest epoch/lowest series'),
            (u'latestEpochOrHighestSeries', u'Latest epoch/highest series'),
            (u'earliestAgeOrLowestStage', u'Earliest age/lowest stage'),
            (u'latestAgeOrHighestStage', u'Latest age/highest stage'),
            (u'lowestBiostratigraphicZone', u'Lowest biostratigraphic zone'),
            (u'highestBiostratigraphicZone', u'Highest biostratigraphic zone'),
            (u'group', u'Group'),
            (u'formation', u'Formation'),
            (u'member', u'Member'),
            (u'bed', u'Bed'),
            (u'chronostratigraphy', u'Chronostratigraphy'),
            (u'lithostratigraphy', u'Lithostratigraphy'),
            ])),
        (u'Meteorites', OrderedDict([
            (u'meteoriteType', u'Meteorite type'),
            (u'meteoriteGroup', u'Meteorite group'),
            (u'chondriteAchondrite', u'Chondrite Achondrite'),
            (u'meteoriteClass', u'Meteorite class'),
            (u'petrologyType', u'Petrology type'),
            (u'petrologySubtype', u'Petrology subtype'),
            (u'recovery', u'Recovery'),
            (u'recoveryDate', u'Recovery date'),
            (u'recoveryWeight', u'Recovery weight'),
            # "Registered weight unit",  # Merged into Registered weight
            ])),
        (u'Botany', OrderedDict([
            (u'exsiccata', u'Exsiccata'),
            (u'exsiccataNumber', u'Exsiccata number'),
            (u'plantDescription', u'Plant description'),
            (u'cultivated', u'Cultivated'),
            ])),
        (u'Zoology', OrderedDict([
            (u'populationCode', u'Population code'),
            (u'nestShape', u'Nest shape'),
            (u'nestSite', u'Nest site'),
            (u'clutchSize', u'Clutch size'),
            (u'setMark', u'Set mark'),
            (u'barcode', u'Barcode'),
            (u'extractionMethod', u'Extraction method'),
            (u'resuspendedIn', u'Resuspended in'),
            (u'totalVolume', u'Total volume'),
            (u'partType', u'Part type'),
            ])),
        (u'Record', OrderedDict([
            (u'occurrenceID', u'Occurrence ID'),
            (u'modified', u'Modified'),
            (u'created', u'Created'),
            (u'recordType', u'Record type')
            ])),
        ])

    def render_record(self, c):
        '''Render a record
        Called from record controller, when viewing a record page

        :param c: 
        :returns: html

        '''

        occurrence_id = c.record_dict.get(u'occurrenceID')

        log.info(u'Viewing record %s', occurrence_id)

        c.record_title = c.record_dict.get(u'catalogNumber', None) or occurrence_id

        # Act on a deep copy of field groups, so deleting element will not have
        # any impact
        c.field_groups = deepcopy(self.field_groups)

        # Some fields are being merged together - in which case we'll need custom filters
        # This can be set to bool false to not display a filter
        c.custom_filters = {}

        if c.record_dict.get(u'registeredWeight', None) and c.record_dict.get(
                u'registeredWeightUnit', None):
            # Create custom filter which acts on both weight and units
            c.custom_filters[
                u'registeredWeight'] = u'registeredWeight:%s|registeredWeightUnit:%s' % (
                c.record_dict[u'registeredWeight'],
                c.record_dict[u'registeredWeightUnit'])
            # Merge unit into the field
            c.record_dict[u'registeredWeight'] += u' %s' % c.record_dict[
                u'registeredWeightUnit']

        collection_date = []
        collection_date_filter = []

        # Merge day, month, year into one collection date field
        for k in (u'day', u'month', u'year'):
            # Delete the exists field
            try:
                del c.field_groups[u'Collection event'][k]
            except KeyError:
                pass

            # Add to collection date field
            if c.record_dict.get(k, None):
                collection_date.append(c.record_dict.get(k))
                collection_date_filter.append(u'%s:%s' % (k, c.record_dict.get(k)))

        # Join the date for the record view
        c.record_dict[u'collectionDate'] = u' / '.join(collection_date)

        # Create a custom filter, so collection date filters on day, month and year
        c.custom_filters[u'collectionDate'] = u'|'.join(collection_date_filter)

        c.field_groups[u'Collection event'][u'collectionDate'] = u'Collection date'

        # Parse determination names
        c.record_dict[u'determinations'] = {}
        c.record_dict[u'determination_labels'] = []

        for field in [u'determinationNames', u'determinationTypes',
                      u'determinationFiledAs']:

            label = field.replace(u'determination', u'')
            # Add a space before capital letters
            label = re.sub(u'([A-Z])"', u' \1"', label)

            c.record_dict[u'determination_labels'].append(label)
            value = c.record_dict.get(field, None)
            if not value:
                value = []
            elif not isinstance(value, list):
                value = [value]
            c.record_dict['determinations'][label] = value

        c.record_dict[u'determinations'][u'_len'] = max(
            [len(l) for l in c.record_dict[u'determinations'].values()])

        # Set determinations to None if we don't have any values - required by the
        # specimen template
        # to hide the Identification block
        if not c.record_dict[u'determinations'][u'_len']:
            c.record_dict[u'determinations'] = None

        # No filters for determinations
        c.custom_filters[u'determinations'] = None

        return toolkit.render(u'record/specimen.html')
