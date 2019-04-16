import json
import logging
import ckan.plugins as p
import ckan.lib.navl.dictization_functions
import ckanext.nhm.logic.schema as nhm_schema
import ckan.logic as logic
import ckan.model as model
from ckan.common import c
from ckanext.nhm.lib.mam import mam_media_request
from ckanext.nhm.dcat.processors import RDFSerializer
from ckanext.nhm.lib.record import get_record_by_uuid

NotFound = logic.NotFound
ActionError = logic.ActionError
get_action = logic.get_action
_get_or_bust = logic.get_or_bust
_validate = ckan.lib.navl.dictization_functions.validate

log = logging.getLogger(__name__)


def record_show(context, data_dict):

    """
    Retrieve an individual record
    @param context:
    @param data_dict:
    @return:
    """
    # Validate the data
    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    schema = context.get('schema', nhm_schema.record_show_schema())
    data_dict, errors = _validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    resource_id = _get_or_bust(data_dict, 'resource_id')
    record_id = _get_or_bust(data_dict, 'record_id')

    # Retrieve datastore record
    record_data_dict = {'resource_id': resource_id, 'filters': {'_id': record_id}}
    if 'version' in data_dict:
        record_data_dict['version'] = data_dict['version']
    search_result = get_action('datastore_search')(context, record_data_dict)

    try:
        record = {
            'data': search_result['records'][0],
            'fields': search_result['fields'],
            'resource_id': resource_id
        }
    except IndexError:
        # If we don't have a result, raise not found
        raise NotFound

    return record


def download_original_image(context, data_dict):

    """
    Request an original image from the MAM
    Before sending request, performs a number of checks
        - The resource exists
        - The record exists on that resource
        - And the image exists on that record
    @param context:
    @param data_dict:
    @return:
    """

    # Validate the data
    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    schema = context.get('schema', nhm_schema.download_original_image_schema())
    data_dict, errors = _validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    # Get the resource
    resource = p.toolkit.get_action('resource_show')(context, {'id': data_dict['resource_id']})

    # Retrieve datastore record
    search_result = get_action('datastore_search')(context, {'resource_id': data_dict['resource_id'], 'filters': {'_id': data_dict['record_id']}})

    try:
        record = search_result['records'][0]
    except IndexError:
        # If we don't have a result, raise not found
        raise NotFound

    if not _image_exists_on_record(resource, record, data_dict['asset_id']):
        raise NotFound

    try:
        mam_media_request(data_dict['asset_id'], data_dict['email'])
    except Exception, e:
        log.error(e)
        raise ActionError('Could not request original')
    else:
        return 'Original image request successful'


def object_rdf(context, data_dict):
    """
    Get record RDF
    :param context:
    :param data_dict:
    :return:
    """
    # validate the data
    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    schema = context.get('schema', nhm_schema.object_rdf_schema())
    data_dict, errors = _validate(data_dict, schema, context)
    # raise any validation errors
    if errors:
        raise p.toolkit.ValidationError(errors)

    # get the record
    version = data_dict.get(u'version', None)
    record_dict, resource_dict = get_record_by_uuid(data_dict['uuid'], version)
    if record_dict:
        record_dict['uuid'] = data_dict['uuid']
        serializer = RDFSerializer()
        output = serializer.serialize_record(record_dict, resource_dict,
                                             _format=data_dict.get('format'))
        return output
    raise NotFound


def _image_exists_on_record(resource, record, asset_id):
    """
    Check the image belongs to the record
    :param resource:
    :param record:
    :param asset_id:
    :return:
    """
    # FIXME - If no image field use gallery
    image_field = resource.get('_image_field', None)

    # Check the asset ID belongs to the record
    for image in record[image_field]:
        url = image.get('identifier', None)
        if asset_id in url:
            return True
    return False
