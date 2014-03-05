import pylons
import ckan.lib.base as base
import ckan.plugins as p
from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.lib.render import find_template
from ckanext.nhm.controllers.record import RecordController
import logging

log = logging.getLogger(__name__)

class KeEMuRecordController(RecordController):
    """
    Controller for displaying KE EMu records
    """

    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """
        # Try and get the record
        c.record_dict = self._get_record(package_name, resource_id, record_id)
        return p.toolkit.render('record/view.html')

    def view_dwc(self, package_name, resource_id, record_id):
        """
        View the record as DwC
        @param id: dataset name string
        @param resource_id: id uuid
        @param record_id: int (irn)
        """
        pass



