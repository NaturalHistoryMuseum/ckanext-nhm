from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
from ckanext.nhm.lib.dwc import DwC

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

class DarwinCoreController(base.BaseController):
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
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(context, {'id': resource_id})

            if c.resource['format'] != 'dwc':
                abort(404, _('No Darwin Core record found'))

            c.package = get_action('package_show')(context, {'id': package_name})
            # required for nav menu
            c.pkg = context['package']
            c.pkg_dict = c.package
            c.record_dict = get_action('record_get')(context, {'resource_id': resource_id, 'record_id': record_id, 'dwc': True})
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

<<<<<<< HEAD
        return p.toolkit.render('dwc/view.html', extra_vars={
            'DwC': DwC,
        })





=======
        return p.toolkit.render('dwc/view.html')
>>>>>>> ckan-1251-1725-custom
