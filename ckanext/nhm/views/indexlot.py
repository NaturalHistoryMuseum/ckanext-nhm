#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from collections import OrderedDict

from ckanext.nhm.lib.filter_options import has_image
from ckanext.nhm.views.default import DefaultView

from ckan.plugins import toolkit

log = logging.getLogger(__name__)


class IndexLotView(DefaultView):
    '''Controller for displaying a specimen record'''

    resource_id = toolkit.config.get(u'ckanext.nhm.indexlot_resource_id')

    field_facets = [
        'family',
        'type',
        'taxonRank',
        'associatedMedia.category',
        'kindOfMaterial'
        ]

    # Additional search filter options
    filter_options = [has_image]

    field_groups = OrderedDict(
        [(u'Classification', OrderedDict(
            [(u'currentScientificName', u'Scientific name'),
             (u'scientificNameAuthorship', u'Author'),
             (u'kingdom', u'Kingdom'),
             (u'phylum', u'Phylum'), (u'class', u'Class'),
             (u'order', u'Order'),
             (u'family', u'Family'), (u'genus', u'Genus'),
             (u'subgenus', u'Subgenus'),
             (u'specificEpithet', u'Species'),
             (u'infraspecificEpithet', u'Subspecies'),
             (u'higherClassification', u'Higher classification'),
             (u'taxonRank', u'Taxon rank'), ])),
         (u'Specimen', OrderedDict(
             [(u'type', u'Type'),
              (u'media', u'Media'),
              (u'british', u'British'), ])),
         (u'Material details', OrderedDict(
             [(u'material', u'Material'),
              (u'kindOfMaterial', u'Kind of material'),
              (u'kindOfMedia', u'Kind of media'),
              (u'materialCount', u'Count'),
              (u'materialSex', u'Sex'),
              (u'materialStage', u'Stage'),
              (u'materialTypes', u'Types'),
              (u'materialPrimaryTypeNumber', u'Primary type number'), ])),
         (u'Record', OrderedDict([
             (u'GUID', u'GUID'),
             (u'modified', u'Modified'),
             (u'created', u'Created'), ])), ])

    def render_record(self, c):
        '''

        :param c: 

        '''
        c.field_groups = self.field_groups
        return toolkit.render(u'record/collection.html')
