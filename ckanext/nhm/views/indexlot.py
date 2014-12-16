import ckan.logic as logic
import ckan.lib.base as base
import logging
from ckanext.nhm.views.default import DefaultView
from pylons import config
import ckan.plugins as p

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class IndexLotView(DefaultView):
    """
    Controller for displaying a specimen record
    """

    resource_id = config.get("ckanext.nhm.indexlot_resource_id")

    def render_record(self, c):
        return p.toolkit.render('record/indexlot.html')

