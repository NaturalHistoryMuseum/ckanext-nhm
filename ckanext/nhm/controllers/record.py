from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import OrderedDict, _, json, request, c, g, response
import logging

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

class RecordController(base.BaseController):
    """
    Controller for displaying an individual record
    """

    @staticmethod
    def _get_record(package_name, resource_id, record_id):

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(context, {'id': resource_id})
            c.package = get_action('package_show')(context, {'id': package_name})
            # required for nav menu
            c.pkg = context['package']
            c.pkg_dict = c.package
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        # Try and get the record
        record = get_action('record_get')(context, {'resource_id': resource_id, 'record_id': record_id})

        if not record:
            abort(404, _('Record not found'))

        return record

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


