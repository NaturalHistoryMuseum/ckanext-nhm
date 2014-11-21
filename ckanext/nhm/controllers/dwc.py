from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
import re
from ckanext.nhm.lib.dwc import DwC
from ckanext.nhm.controllers.record import RecordController

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class DarwinCoreController(RecordController):
    """
    Controller for displaying KE EMu records as DwC
    """

    format = 'dwc'

    dwc = DwC()

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

    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        self._load_data(package_name, resource_id, record_id)

        # FIXME
        c.dwc = DwC(**c.record_dict)

        if c.resource['format'].lower() != 'dwc':
            abort(404, _('Record not in Darwin Core format'))

        return p.toolkit.render('dwc/view.html')

    def get_field_groups(self):

        return self.dwc.terms

