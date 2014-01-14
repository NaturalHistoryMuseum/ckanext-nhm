import ckan.plugins as p
import ckan.lib.navl.dictization_functions
import ckanext.nhm.logic.schema as nhm_schema
import ckan.logic as logic
import ckan.model as model
from ckan.common import c
import pylons
from ckanext.datastore.logic.action import _resource_exists

get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

def resource_exists(context, data_dict):

    """
    Check if a resource exists
    A wrapper around _resource_exists - the existing _resource_exists action is private
    @param context:
    @param data_dict:
    @return:
    """
    if 'id' in data_dict:
        data_dict['resource_id'] = data_dict['id']

    data_dict['connection_url'] = pylons.config['ckan.datastore.write_url']

    return _resource_exists(context, data_dict)

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

    search_result = get_action('datastore_search')(context, {'resource_id': data_dict['resource_id'], 'filters': {'_id': data_dict['record_id']}})

    try:
        return search_result['records'].pop()
    except IndexError:
        pass