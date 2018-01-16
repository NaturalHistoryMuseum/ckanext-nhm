#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK



import ckan.logic as logic
import ckan.plugins as p
from ckan.common import _
import ckan.lib.base as base
import logging
from ckan.lib import helpers as h

import re
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.lib.dwc import dwc_terms

log = logging.getLogger(__name__)

abort = base.abort

get_action = logic.get_action


class DarwinCoreView(DefaultView):
    '''View for displaying DwC resources'''

    format = u'dwc'

    grid_default_columns = [
        u'_id',
        u'gbifIssue',
        u'scientificName',
        u'scientificNameAuthorship',
        u'specificEpithet',
        u'infraspecificEpithet',
        u'family',
        u'genus',
        u'class',
        u'locality',
        u'country',
        u'viceCounty',
        u'recordedBy',
        u'typeStatus',
        u'catalogNumber',
        u'collectionCode'
    ]

    grid_column_widths = {
        u'gbifIssue': 70,
        u'catalogNumber': 120,
        u'scientificNameAuthorship': 180,
        u'scientificName': 160
    }

    def render_record(self, c):
        '''

        :param c: 

        '''

        if c.resource[u'format'].lower() != u'dwc':
            abort(404, _(u'Record not in Darwin Core format'))

        c.record_title = c.record_dict.get(u'catalogNumber', None) or c.record_dict.get(u'occurrenceID')
        fields = h.resource_view_get_fields(c.resource)
        c.dwc_terms = dwc_terms(fields)

        try:
            c.dynamic_properties = c.dwc_terms.pop(u'dynamicProperties')
        except IndexError:
            c.dynamic_properties = []

        return p.toolkit.render(u'record/dwc.html')
