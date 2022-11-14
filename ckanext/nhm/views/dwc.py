#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging

from ckan.plugins import toolkit

from ckanext.nhm.lib.dwc import dwc_terms
from ckanext.nhm.views.default import DefaultView

log = logging.getLogger(__name__)


class DarwinCoreView(DefaultView):
    """
    View for displaying DwC resources.
    """

    format = 'dwc'

    grid_default_columns = [
        '_id',
        'gbifIssue',
        'scientificName',
        'scientificNameAuthorship',
        'specificEpithet',
        'infraspecificEpithet',
        'family',
        'genus',
        'class',
        'locality',
        'country',
        'viceCounty',
        'recordedBy',
        'typeStatus',
        'catalogNumber',
        'collectionCode',
    ]

    grid_column_widths = {
        'gbifIssue': 70,
        'catalogNumber': 120,
        'scientificNameAuthorship': 180,
        'scientificName': 160,
    }

    def render_record(self, c):
        '''

        :param c:

        '''

        if c.resource['format'].lower() != 'dwc':
            toolkit.abort(404, toolkit._('Record not in Darwin Core format'))

        c.record_title = c.record_dict.get('catalogNumber', None) or c.record_dict.get(
            'occurrenceID'
        )
        fields = toolkit.h.resource_view_get_fields(c.resource)
        c.dwc_terms = dwc_terms(fields)

        try:
            c.dynamic_properties = c.dwc_terms.pop('dynamicProperties')
        except IndexError:
            c.dynamic_properties = []

        return toolkit.render('record/dwc.html')
