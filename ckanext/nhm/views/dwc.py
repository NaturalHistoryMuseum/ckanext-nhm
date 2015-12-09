

import ckan.logic as logic
import ckan.plugins as p
from ckan.common import _
import ckan.lib.base as base
import logging
import os
from lxml import etree

import re
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.lib.resource import resource_get_ordered_fields
from ckanext.nhm.lib.dwc import dwc_terms

log = logging.getLogger(__name__)

abort = base.abort

get_action = logic.get_action


class DarwinCoreView(DefaultView):
    """
    View for displaying DwC resources
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
        'viceCountry',
        'recordedBy',
        'typeStatus',
        'catalogNumber',
        'collectionCode'
    ]

    grid_column_widths = {
        'gbifIssue': 70,
        'catalogNumber': 120,
        'scientificNameAuthorship': 180,
        'scientificName': 160
    }

    def render_record(self, c):

        if c.resource['format'].lower() != 'dwc':
            abort(404, _('Record not in Darwin Core format'))

        c.record_title = c.record_dict.get('catalogNumber', None) or c.record_dict.get('occurrenceID')
        c.dwc_terms = dwc_terms(c.record_dict.keys())

        try:
            c.dynamic_properties = c.dwc_terms.pop('dynamicProperties')
        except IndexError:
            c.dynamic_properties = []

        return p.toolkit.render('record/dwc.html')