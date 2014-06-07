from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
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
    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        self._load_data(package_name, resource_id, record_id)

        c.dwc = DwC(**c.record_dict)

        if c.resource['format'] != 'dwc':
            abort(404, _('Record not in Darwin Core format'))

        return p.toolkit.render('dwc/view.html')