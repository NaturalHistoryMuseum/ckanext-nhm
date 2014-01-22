from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.lib.jsonp import jsonpify
import logging

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

class MapController(base.BaseController):
    """
    Temporary for displaying a map
    This will be replaced as part of the OKF work
    """

    @jsonpify
    def view(self, resource_id):

        """
        View a map
        :param id:
        :param resource_id:
        :return: json
        """
        c.filters = request.POST.items()

        # TODO: Q matches _full_text

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(context, {'id': resource_id})
        except NotFound:
            html = 'Resource not found'
        else:
            html = p.toolkit.render('map/view.html')

        return {"html": html}




