#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import ckan.logic as logic
import ckan.lib.base as base
import logging
from ckanext.nhm.views.default import DefaultView
from pylons import config
import ckan.plugins as p
from collections import OrderedDict

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class IndexLotView(DefaultView):
    '''Controller for displaying a specimen record'''

    resource_id = config.get(u'ckanext.nhm.indexlot_resource_id')

    field_facets = [
        u'family',
        u'type',
        u'taxonRank',
        u'imageCategory',
        u'kindOfMaterial'
    ]

    # Additional search filter options
    filter_options = {
        u'_has_image': {
            u'label': u'Has images',
            u'solr': u'_has_multimedia:true'
        },
    }

    field_groups = OrderedDict([
        (u'Classification', OrderedDict([
            (u'currentScientificName', u'Scientific name'),
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
        (u'Specimen', OrderedDict([
            (u'type', u'Type'),
            (u'media', u'Media'),
            (u'british', u'British'),
        ])),
        (u'Material details', OrderedDict([
            (u'material', u'Material'),
            (u'kindOfMaterial', u'Kind of material'),
            (u'kindOfMedia', u'Kind of media'),
            (u'materialCount', u'Count'),
            (u'materialSex', u'Sex'),
            (u'materialStage', u'Stage'),
            (u'materialTypes', u'Types'),
            (u'materialPrimaryTypeNumber', u'Primary type number'),
        ])),
        (u'Record', OrderedDict([
            (u'GUID', u'GUID'),
            (u'modified', u'Modified'),
            (u'created', u'Created'),
        ])),
    ])

    def render_record(self, c):
        '''

        :param c: 

        '''
        c.field_groups = self.field_groups
        return p.toolkit.render(u'record/collection.html')
