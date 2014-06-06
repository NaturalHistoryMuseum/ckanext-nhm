from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
from ckan.lib.render import find_template

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

    def _load_data(self, package_name, resource_id, record_id):
        """
        Load the data for dataset, resource and record (into C var)
        @param package_name:
        @param resource_id:
        @param record_id:
        @return:
        """

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(context, {'id': resource_id})
            c.package = get_action('package_show')(context, {'id': package_name})
            # required for nav menu
            c.pkg = context['package']
            c.pkg_dict = c.package
            c.record_dict = get_action('record_get')(context, {'resource_id': resource_id, 'record_id': record_id})

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        self._load_data(package_name, resource_id, record_id)

        # Try and use a template file based on the resource name
        template_file = 'record/{dataset}_{resource}.html'.format(
            # TEMP: Change this
            # dataset=c.package['name'].lower(),
            dataset='collection',
            resource=c.resource['name'].lower()
        )

        if not find_template(template_file):
            # If we don't have a specific template file, use the generic one
            template_file = 'record/view.html'

        return p.toolkit.render(template_file)


