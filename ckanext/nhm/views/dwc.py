

import ckan.logic as logic
import ckan.plugins as p
from ckan.common import _
import ckan.lib.base as base
import logging
import os
from lxml import etree
from collections import OrderedDict
import re
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.lib.resource import resource_get_ordered_fields

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
        'catalogNumber': 120,
        'scientificNameAuthorship': 180,
        'scientificName': 160
    }

    # All DwC terms
    terms = OrderedDict()

    uris = {}

    def __init__(self, **kwargs):

        # Read the DwC terms XSD to populate terms and groups
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'tdwg_dwcterms.xsd')

        data = etree.parse(open(f), etree.XMLParser())
        root = data.getroot()

        for group in root.iterfind("xs:group", namespaces=root.nsmap):

            group_label = self._group_label(group.get('name'))

            # Create a list for the group terms
            group_terms = OrderedDict()

            for term in group.iterfind("xs:sequence/xs:element", namespaces=root.nsmap):

                ns, name = term.get("ref").split(':')

                # Add URI
                self.uris[name] = '{ns}{name}'.format(ns=root.nsmap[ns], name=name)

                # Add to group terms
                group_terms[name] = self._field_label(name)

            # If we have terms for this group, add the group
            # We don't want empty groups
            if group_terms:
                self.terms[group_label] = group_terms

    @staticmethod
    def _group_label(group_name):
        """
        Get a label for the group
        Takes the original group name, removes Term, de-pluralises and splits on capital
        GeologicalContextsTerm => Geological Contexts
        @param group: Original group name
        @return: label
        """
        label = ' '.join(re.findall('[A-Z][a-z]*', group_name.replace('Term', '')))

        if label.endswith('s'):
            label = label[:-1]

        return label

    @staticmethod
    def _field_label(field):

        label = re.sub('([A-Z]+)', r' \1', field).capitalize()
        label = label.replace(' id', ' ID')
        return label

    def render_record(self, c):

        if c.resource['format'].lower() != 'dwc':
            abort(404, _('Record not in Darwin Core format'))

        c.record_title = c.record_dict.get('catalogNumber', None) or c.record_dict.get('occurrenceID')
        c.field_groups = self.get_field_groups(c.resource)
        c.uris = self.uris

        return p.toolkit.render('record/dwc.html')

    def get_field_groups(self, resource):

        # For DwC we want to limit the field and groups to only those
        # In the dataset, as not all datasets will use all fields
        resource_fields = resource_get_ordered_fields(resource['id'])

        for group, terms in self.terms.items():
            for term in terms:
                if term not in resource_fields:
                    del self.terms[group][term]

                    # And delete and empty groups
                    if not self.terms[group]:
                        del self.terms[group]

        return self.terms