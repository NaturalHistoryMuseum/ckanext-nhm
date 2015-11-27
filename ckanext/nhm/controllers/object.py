import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
from ckan.common import _, c
import ckan.lib.helpers as h
import ckan.plugins as p
import logging
from ckanext.nhm.lib.helpers import get_specimen_resource_id
from ckan.controllers.home import HomeController
from ckanext.dcat.utils import CONTENT_TYPES
from ckanext.dcat.controllers import check_access_header

log = logging.getLogger(__name__)

abort = base.abort
get_action = logic.get_action


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

    def _get_object(self, uuid):

        # Loop through all resources, and try and find the record
        # Need to loop as this works for all specimens, indexlots and artefacts

        resource_ids = [get_specimen_resource_id()]

        for resource_id in resource_ids:

            try:
                # Load the resource via model so we have access to get_package_id
                resource = model.Resource.get(resource_id)
                # Retrieve datastore record
                search_result = get_action('datastore_search')(self.context, {'resource_id': resource_id, 'filters': {'occurrenceID': uuid}})
                record = search_result['records'][0]
            except:
                pass
            else:
                return resource, record


    def redirect(self, uuid):
        """
        Redirect to object associated with UUID
        """

        # FIXME - Need to add in indexlots and artefacts

        resource, record = self._get_object(uuid)

        if record:

            package_id = resource.get_package_id()

            package = get_action('package_show')(self.context, {'id': package_id})

            h.redirect_to(controller='ckanext.nhm.controllers.record:RecordController', action='view', package_name=package['name'], resource_id=resource['id'], record_id=record['_id'])

        abort(404, _('Record not found'))

    def rdf(self, uuid, _format=None):
        """
        Return RDF
        :param uuid:
        :param _format:
        :return:
        """

        resource, record = self._get_object(uuid)

        if not record:
            abort(404, _('Record not found'))

        if not _format:
            _format = check_access_header()

        if not _format:
            return HomeController().index()

        data_dict = {
            'record_id': record['_id'],
            'resource_id': resource.id,
            'format': _format,
        }

        p.toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        try:
            return p.toolkit.get_action('object_rdf')(self.context, data_dict)
        except p.toolkit.ValidationError, e:
            p.toolkit.abort(409, str(e))