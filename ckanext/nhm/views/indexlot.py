import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins as p
from ckan.common import _, c
import logging
import re
from ckanext.nhm.controllers.record import RecordController
from pylons import config
from collections import OrderedDict

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class IndexLotController(RecordController):
    """
    Controller for displaying a specimen record
    """

    resource_id = config.get("ckanext.nhm.indexlot_resource_id")

    def render_record(self):
        pass

