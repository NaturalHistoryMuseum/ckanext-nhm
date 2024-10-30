#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from collections import OrderedDict

from ckan.plugins import toolkit

from ckanext.nhm.lib.filter_options import has_image
from ckanext.nhm.views.default import DefaultView

log = logging.getLogger(__name__)


def modify_field_groups(field_groups):
    """
    Given a FieldGroups object from the vds plugin, force certain field groups to show
    in multisearch results and force certain field groups to be ignored and not shown.

    :param field_groups: a FieldGroups object
    """
    # forces
    field_groups.force("scientificName")
    field_groups.force("family")
    field_groups.force("typeStatus")
    field_groups.force("locality")
    field_groups.force("country")
    field_groups.force("recordedBy")
    field_groups.force("catalogNumber")
    field_groups.force("associatedMediaCount")
    field_groups.force("preservative")
    field_groups.force("collectionCode")
    field_groups.force("year")
    field_groups.force("month")
    field_groups.force("day")
    # ignores
    field_groups.ignore("created")
    field_groups.ignore("modified")
    field_groups.ignore("basisOfRecord")
    field_groups.ignore("institutionCode")
    field_groups.ignore("associatedMedia.*")
    field_groups.ignore("barcode")


class IndexLotView(DefaultView):
    """
    Controller for displaying a specimen record.
    """

    resource_id = toolkit.config.get('ckanext.nhm.indexlot_resource_id')

    field_facets = [
        'family',
        'type',
        'taxonRank',
        'associatedMedia.category',
        'kindOfMaterial',
    ]

    # Additional search filter options
    filter_options = [has_image]

    field_groups = OrderedDict(
        [
            (
                'Classification',
                OrderedDict(
                    [
                        ('currentScientificName', 'Scientific name'),
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
                'Specimen',
                OrderedDict(
                    [
                        ('type', 'Type'),
                        ('media', 'Media'),
                        ('british', 'British'),
                    ]
                ),
            ),
            (
                'Material details',
                OrderedDict(
                    [
                        ('material', 'Material'),
                        ('kindOfMaterial', 'Kind of material'),
                        ('kindOfMedia', 'Kind of media'),
                        ('materialCount', 'Count'),
                        ('materialSex', 'Sex'),
                        ('materialStage', 'Stage'),
                        ('materialTypes', 'Types'),
                        ('materialPrimaryTypeNumber', 'Primary type number'),
                    ]
                ),
            ),
            (
                'Record',
                OrderedDict(
                    [
                        ('GUID', 'GUID'),
                        ('modified', 'Modified'),
                        ('created', 'Created'),
                    ]
                ),
            ),
        ]
    )

    def render_record(self, c):
        '''

        :param c:

        '''
        c.field_groups = self.field_groups
        return toolkit.render('record/collection.html')
