import ckan.plugins as p
import ckan.lib.navl.dictization_functions
import ckanext.nhm.logic.schema as nhm_schema
import ckan.logic as logic
import ckan.model as model
from ckan.common import c

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
    schema = context.get('schema', nhm_schema.record_get_schema())
    data_dict, errors = _validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    print data_dict['resource_id']
    print data_dict['record_id']

    # Retrieve datastore record
    search_result = get_action('datastore_search')(context, {'resource_id': data_dict['resource_id'], 'filters': {'_id': data_dict['record_id']}})
    try:
        record = search_result['records'][0]
    except IndexError:
        # If we don't have a result, raise not found
        raise NotFound

    return record