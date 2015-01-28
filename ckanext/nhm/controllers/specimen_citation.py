import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
from ckan.common import _, c
import ckan.lib.helpers as h
import logging
from ckanext.nhm.lib.helpers import get_specimen_resource_id

log = logging.getLogger(__name__)

abort = base.abort
get_action = logic.get_action


class SpecimenCitationController(base.BaseController):
    """

    Controller for handling specimen citation URLS

    http://10.11.12.13:5000/specimen/73f450db-46b3-45a0-ac18-f00547be5af1

    Checks record exists, then 302 to the record page

    """

    def view(self, uuid):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        resource_id = get_specimen_resource_id()

        try:
            # Load the resource via model so we have access to get_package_id
            resource = model.Resource.get(resource_id)

            package_id = resource.get_package_id()

            package = get_action('package_show')(context, {'id': package_id})

            # Retrieve datastore record
            search_result = get_action('datastore_search')(context, {'resource_id': resource_id, 'filters': {'occurrenceID': uuid}})
            record = search_result['records'][0]
        except:
            pass
        else:

            h.redirect_to(controller='ckanext.nhm.controllers.record:RecordController', action='view', package_name=package['name'], resource_id=resource_id, record_id=record['_id'])

        abort(404, _('Record not found'))
