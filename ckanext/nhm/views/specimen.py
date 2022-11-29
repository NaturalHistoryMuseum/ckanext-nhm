#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
import re
from collections import OrderedDict
from copy import deepcopy

from ckan.plugins import toolkit

from ckanext.nhm.lib.filter_options import exclude_mineralogy, has_image, has_lat_long
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.views.dwc import DarwinCoreView

log = logging.getLogger(__name__)


class SpecimenView(DefaultView):
    """
    Controller for displaying a specimen record.
    """

    resource_id = toolkit.config.get('ckanext.nhm.specimen_resource_id')

    grid_default_columns = DarwinCoreView.grid_default_columns
    grid_column_widths = DarwinCoreView.grid_column_widths

    field_facets = [
        'collectionCode',
        'typeStatus',
        'family',
        'genus',
        'associatedMedia.category',
        'gbifIssue',
    ]

    # Additional search filter options
    filter_options = [has_image, has_lat_long, exclude_mineralogy]

    field_groups = OrderedDict(
        [
            (
                'Classification',
                OrderedDict(
                    [
                        ('scientificName', 'Scientific name'),
                        ('scientificNameAuthorship', 'Author'),
                        ('kingdom', 'Kingdom'),
                        ('phylum', 'Phylum'),
                        ('class', 'Class'),
                        ('order', 'Order'),
                        ('family', 'Family'),
                        ('genus', 'Genus'),
                        ('subgenus', 'Subgenus'),
                        ('specificEpithet', 'Species'),
                        ('infraspecificEpithet', 'Subspecies'),
                        ('higherClassification', 'Higher classification'),
                        ('taxonRank', 'Taxon rank'),
                    ]
                ),
            ),
            (
                'Location',
                OrderedDict(
                    [
                        ('labelLocality', 'Label locality'),
                        ('locality', 'Locality'),
                        ('stateProvince', 'State province'),
                        ('mine', 'Mine'),
                        ('miningDistrict', 'Mining district'),
                        ('viceCounty', 'Vice County'),
                        ('country', 'Country'),
                        ('continent', 'Continent'),
                        ('island', 'Island'),
                        ('islandGroup', 'Island group'),
                        ('waterBody', 'Water body'),
                        ('higherGeography', 'Higher geography'),
                        ('decimalLatitude', 'Decimal latitude'),
                        ('decimalLongitude', 'Decimal longitude'),
                        ('verbatimLatitude', 'Verbatim latitude'),
                        ('verbatimLongitude', 'Verbatim longitude'),
                        ('coordinateUncertaintyInMeters', 'Coordinate uncertainty'),
                        ('centroid', 'Centroid'),
                        ('maxError', 'Max error'),
                        ('geodeticDatum', 'Geodetic datum'),
                        ('georeferenceProtocol', 'Georeference protocol'),
                        ('minimumElevationInMeters', 'Minimum elevation(m)'),
                        ('maximumElevationInMeters', 'Maximum elevation(m)'),
                        ('minimumDepthInMeters', 'Minimum depth(m)'),
                        ('maximumDepthInMeters', 'Maximum depth(m)'),
                    ]
                ),
            ),
            (
                'Collection event',
                OrderedDict(
                    [
                        ('recordedBy', 'Recorded by'),
                        ('recordNumber', 'Record number'),
                        ('year', 'Year'),
                        ('month', 'Month'),
                        ('day', 'Day'),
                        ('eventTime', 'Event time'),
                        ('expedition', 'Expedition'),
                        ('habitat', 'Habitat'),
                        ('vessel', 'Vessel'),
                        ('samplingProtocol', 'Sampling protocol'),
                    ]
                ),
            ),
            (
                'Identification',
                OrderedDict(
                    [
                        ('identifiedBy', 'Identified by'),
                        ('dateIdentified', 'Date identified'),
                        ('identificationQualifier', 'Identification qualifier'),
                        ('typeStatus', 'Type status'),
                        ('determinations', 'Determinations'),
                    ]
                ),
            ),
            (
                'Specimen',
                OrderedDict(
                    [
                        ('catalogNumber', 'Catalogue number'),
                        ('collectionCode', 'Collection code'),
                        ('subDepartment', 'Sub department'),
                        ('otherCatalogNumbers', 'Other catalog numbers'),
                        ('registrationCode', 'Registration code'),
                        ('kindOfObject', 'Kind of object'),
                        ('preparations', 'Preparations'),
                        ('preparationType', 'Preparation type'),
                        ('preservative', 'Preservative'),
                        ('collectionKind', 'Collection kind'),
                        ('collectionName', 'Collection name'),
                        ('donorName', 'Donor name'),
                        ('kindOfCollection', 'Kind of collection'),
                        ('observedWeight', 'Observed weight'),
                        ('individualCount', 'Individual count'),
                        ('sex', 'Sex'),
                        ('lifeStage', 'Life stage'),
                        ('catalogueDescription', 'Catalogue description'),
                    ]
                ),
            ),
            (
                'Mineralogy',
                OrderedDict(
                    [
                        ('dateRegistered', 'Date registered'),
                        ('occurrence', 'Occurrence'),
                        ('commodity', 'Commodity'),
                        ('depositType', 'Deposit type'),
                        ('texture', 'Texture'),
                        ('identificationAsRegistered', 'Identification as registered'),
                        ('identificationDescription', 'Identification description'),
                        ('identificationVariety', 'Identification variety'),
                        ('identificationOther', 'Identification other'),
                        ('hostRock', 'Host rock'),
                        ('age', 'Age'),
                        ('ageType', 'Age type'),
                        ('geologyRegion', 'Geology region'),
                        ('mineralComplex', 'Mineral complex'),
                        ('tectonicProvince', 'Tectonic province'),
                        ('registeredWeight', 'Registered weight'),
                    ]
                ),
            ),
            (
                'Stratigraphy',
                OrderedDict(
                    [
                        ('earliestEonOrLowestEonothem', 'Earliest eon/lowest eonothem'),
                        ('latestEonOrHighestEonothem', 'Latest eon/highest eonothem'),
                        ('earliestEraOrLowestErathem', 'Earliest era/lowest erathem'),
                        ('latestEraOrHighestErathem', 'Latest era/highest erathem'),
                        (
                            'earliestPeriodOrLowestSystem',
                            'Earliest period/lowest system',
                        ),
                        ('latestPeriodOrHighestSystem', 'Latest period/highest system'),
                        ('earliestEpochOrLowestSeries', 'Earliest epoch/lowest series'),
                        ('latestEpochOrHighestSeries', 'Latest epoch/highest series'),
                        ('earliestAgeOrLowestStage', 'Earliest age/lowest stage'),
                        ('latestAgeOrHighestStage', 'Latest age/highest stage'),
                        ('lowestBiostratigraphicZone', 'Lowest biostratigraphic zone'),
                        (
                            'highestBiostratigraphicZone',
                            'Highest biostratigraphic zone',
                        ),
                        ('group', 'Group'),
                        ('formation', 'Formation'),
                        ('member', 'Member'),
                        ('bed', 'Bed'),
                        ('chronostratigraphy', 'Chronostratigraphy'),
                        ('lithostratigraphy', 'Lithostratigraphy'),
                    ]
                ),
            ),
            (
                'Meteorites',
                OrderedDict(
                    [
                        ('meteoriteType', 'Meteorite type'),
                        ('meteoriteGroup', 'Meteorite group'),
                        ('chondriteAchondrite', 'Chondrite Achondrite'),
                        ('meteoriteClass', 'Meteorite class'),
                        ('petrologyType', 'Petrology type'),
                        ('petrologySubtype', 'Petrology subtype'),
                        ('recovery', 'Recovery'),
                        ('recoveryDate', 'Recovery date'),
                        ('recoveryWeight', 'Recovery weight'),
                        # "Registered weight unit",  # Merged into Registered weight
                    ]
                ),
            ),
            (
                'Botany',
                OrderedDict(
                    [
                        ('exsiccata', 'Exsiccata'),
                        ('exsiccataNumber', 'Exsiccata number'),
                        ('plantDescription', 'Plant description'),
                        ('cultivated', 'Cultivated'),
                    ]
                ),
            ),
            (
                'Zoology',
                OrderedDict(
                    [
                        ('populationCode', 'Population code'),
                        ('nestShape', 'Nest shape'),
                        ('nestSite', 'Nest site'),
                        ('clutchSize', 'Clutch size'),
                        ('setMark', 'Set mark'),
                        ('barcode', 'Barcode'),
                        ('extractionMethod', 'Extraction method'),
                        ('resuspendedIn', 'Resuspended in'),
                        ('totalVolume', 'Total volume'),
                        ('partType', 'Part type'),
                    ]
                ),
            ),
            (
                'Record',
                OrderedDict(
                    [
                        ('occurrenceID', 'Occurrence ID'),
                        ('modified', 'Modified'),
                        ('created', 'Created'),
                        ('recordType', 'Record type'),
                    ]
                ),
            ),
        ]
    )

    def render_record(self, c):
        """
        Render a record Called from record controller, when viewing a record page.

        :param c:
        :returns: html
        """

        occurrence_id = c.record_dict.get('occurrenceID')

        log.info(f'Viewing record {occurrence_id}')

        c.record_title = c.record_dict.get('catalogNumber', None) or occurrence_id

        # Act on a deep copy of field groups, so deleting element will not have
        # any impact
        c.field_groups = deepcopy(self.field_groups)

        # Some fields are being merged together - in which case we'll need custom filters
        # This can be set to bool false to not display a filter
        c.custom_filters = {}

        if c.record_dict.get('registeredWeight', None) and c.record_dict.get(
            'registeredWeightUnit', None
        ):
            # Create custom filter which acts on both weight and units
            c.custom_filters[
                'registeredWeight'
            ] = f'registeredWeight:{c.record_dict["registeredWeight"]}|registeredWeightUnit:{c.record_dict["registeredWeightUnit"]}'
            # Merge unit into the field
            c.record_dict[
                'registeredWeight'
            ] += f' {c.record_dict["registeredWeightUnit"]}'

        # add a meters unit to the coordinateUncertaintyInMeters value
        coordinate_uncertainty_in_meters = c.record_dict.get(
            'coordinateUncertaintyInMeters'
        )
        if coordinate_uncertainty_in_meters is not None:
            c.record_dict[
                'coordinateUncertaintyInMeters'
            ] = f'{coordinate_uncertainty_in_meters}m'
            c.custom_filters[
                'coordinateUncertaintyInMeters'
            ] = f'coordinateUncertaintyInMeters:{coordinate_uncertainty_in_meters}'

        collection_date = []
        collection_date_filter = []

        # Merge day, month, year into one collection date field
        for k in ('day', 'month', 'year'):
            # Delete the exists field
            try:
                del c.field_groups['Collection event'][k]
            except KeyError:
                pass

            # Add to collection date field
            if c.record_dict.get(k, None):
                collection_date.append(c.record_dict.get(k))
                collection_date_filter.append(f'{k}:{c.record_dict.get(k)}')

        # Join the date for the record view
        c.record_dict['collectionDate'] = ' / '.join(collection_date)

        # Create a custom filter, so collection date filters on day, month and year
        c.custom_filters['collectionDate'] = '|'.join(collection_date_filter)

        c.field_groups['Collection event']['collectionDate'] = 'Collection date'

        # Parse determination names
        c.record_dict['determinations'] = {}
        c.record_dict['determination_labels'] = []

        for field in [
            'determinationNames',
            'determinationTypes',
            'determinationFiledAs',
        ]:
            label = field.replace('determination', '')
            # Add a space before capital letters
            label = re.sub('([A-Z])"', ' \1"', label)

            c.record_dict['determination_labels'].append(label)
            value = c.record_dict.get(field, None)
            if not value:
                value = []
            elif not isinstance(value, list):
                value = [value]
            c.record_dict['determinations'][label] = value

        c.record_dict['determinations']['_len'] = max(
            [len(l) for l in c.record_dict['determinations'].values()]
        )

        # Set determinations to None if we don't have any values - required by the
        # specimen template
        # to hide the Identification block
        if not c.record_dict['determinations']['_len']:
            c.record_dict['determinations'] = None

        # No filters for determinations
        c.custom_filters['determinations'] = None

        return toolkit.render('record/specimen.html')
