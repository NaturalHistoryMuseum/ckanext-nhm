import ckan.plugins as p
import ckan.lib.navl.dictization_functions
import ckanext.nhm.logic.schema as nhm_schema
import ckan.logic as logic
import ckan.model as model
from ckan.common import c
from ckan.logic.auth import get_resource_object
from ckanext.nhm.lib.keemu import KeEMuSpecimensDatastore
from ckanext.nhm.logic import NotDarwinCore

NotFound = logic.NotFound
get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate


def record_get(context, data_dict):

    """
    Retrieve an individual record
    @param context:
    @param data_dict:
    @return:
    """
    # Validate the data
    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    schema = context.get('schema', nhm_schema.nhm_record_get_schema())
    data_dict, errors = _validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    if data_dict.get('dwc', False):

        # Only KE EMu specimen records are DwC enabled - ensure this resource has the correct resource_type
        resource = get_resource_object(context, {'id': data_dict['resource_id']})

        if not resource.resource_type == KeEMuSpecimensDatastore.resource_type: raise NotDarwinCore("No Darwin Core record")

        specimen_datastore = KeEMuSpecimensDatastore()
        record = specimen_datastore.dwc_get_record(data_dict['record_id'])

    else:

        # Retrieve datastore record
        search_result = get_action('datastore_search')(context, {'resource_id': data_dict['resource_id'], 'filters': {'_id': data_dict['record_id']}})
        try:
            record = search_result['records'][0]
        except IndexError:
            # If we don't have a result, raise not found
            raise NotFound

    return record