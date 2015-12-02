import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
from ckan.common import _, c
import ckan.lib.helpers as h
import ckan.plugins as p
import logging
from ckan.controllers.home import HomeController
from ckanext.dcat.utils import CONTENT_TYPES
from ckanext.dcat.controllers import check_access_header
from ckanext.nhm.lib.record import get_record_by_uuid

log = logging.getLogger(__name__)

abort = base.abort
get_action = logic.get_action

# FIXME - specimen, lot, artefact

class ObjectController(base.BaseController):
    """

    Controller for handling stable objects - those with GUIDs in KE EMu

    If someone accesses URL:
        object/73f450db-46b3-45a0-ac18-f00547be5af1
    It will 302 redirect to the specimen, artefact or index lot page

    If a user requests the object in RDF format:
        object/73f450db-46b3-45a0-ac18-f00547be5af1.ttl
    Returns RDF

    """

    def __before__(self, action, **env):

        base.BaseController.__before__(self, action, **env)
        self.context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}

    def view(self, uuid):
        """
        View object
        If this is basic HTTP request, this will redirect to the record
        If the request is for RDF (content negotiation) return the rdf
        """

        # Is the request for a particular format
        _format = check_access_header()

        if _format:
            return self.rdf(uuid, _format)
        else:
            # This is a normal HTTP request, so redirect to the object record
            record, resource = get_record_by_uuid(uuid)

            if record:
                package_id = resource.get_package_id()
                package = get_action('package_show')(self.context, {'id': package_id})
                h.redirect_to(controller='ckanext.nhm.controllers.record:RecordController', action='view', package_name=package['name'], resource_id=resource.id, record_id=record['_id'])

        abort(404, _('Record not found'))

    def rdf(self, uuid, _format):
        """
        Return RDF
        :param uuid:
        :param _format:
        :return:
        """
        data_dict = {
            'uuid': uuid,
            'format': _format,
        }

        p.toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        try:
            return p.toolkit.get_action('object_rdf')(self.context, data_dict)
        except p.toolkit.ValidationError, e:
            p.toolkit.abort(409, str(e))