# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

'''
Routes for handling stable objects - those with GUIDs in KE EMu

If someone accesses URL:
    object/73f450db-46b3-45a0-ac18-f00547be5af1
It will 302 redirect to the specimen, artefact or index lot page (though currently we only support
specimens).

If a user requests the object in RDF format:
    object/73f450db-46b3-45a0-ac18-f00547be5af1.ttl
Returns RDF

In both cases, if a version is appended to the end of the URL then that version of the record is
returned. For example:
    object/73f450db-46b3-45a0-ac18-f00547be5af1/1551692486000
otherwise the current version is returned.

Old style /specimen urls are also supported to ensure backwards compatibility.
'''

import logging

from ckan.plugins import toolkit
from ckanext.dcat.utils import CONTENT_TYPES, check_access_header
from flask import Blueprint, Response, redirect, url_for

from ckanext.nhm.lib.record import get_record_by_uuid, Record

log = logging.getLogger(__name__)

ABYSSLINE_UUIDS = {
    'bc03fc1a-3613-41a2-b1f1-bf905e0fa6d0',
    'de4bd6ce-07fe-496e-bffc-67a4c6b9782c',
    '16599946-2aba-4710-98e6-43c522061878',
    'b7ffe7a2-7be1-4d4f-b784-7aaecf0ee743',
    '76acc5a2-6e0e-4599-8104-b8e243af10c4',
    '7e8ca2d8-aea1-45bd-b7e0-d0575cadd82d',
    '95d0bd7f-0df9-47e4-8003-cd12007d54b4',
    'c57f1bd3-1b32-41e6-8e1d-0ad6472e4327',
    'd15a68e0-b2b3-40b4-8cab-0563609cc80d',
    '4ae2430e-549e-47f2-ba5d-0e9a08443d31',
    'b2a871bf-46d5-4639-a839-427a3efa848c',
    '280c758b-5287-4a13-9f45-f6a6150b37d0',
    '92825c07-a16d-4c5e-a8e9-4fbcdc8cf44a',
    '2866f91e-b99e-4703-a9d3-fe1876df1da1',
    'd0062182-89dc-4deb-b746-688289783b5f',
    '38c16bec-7bf9-4c2b-b862-5da460ba6c0c',
    '15e6ddc7-3ca7-453c-bba5-f84888716505',
    '72db478a-ea4f-4f3e-be08-95ec9fb4d20e',
    '11948cb9-654f-4519-a654-f134380093ea',
    '292bd655-83d6-440f-9668-82dfa4185b04',
    '2ed865af-1605-4d78-8fd8-9c7659781854',
    '4d6f6aaf-93fd-4629-b224-2ce8dd3320f6',
    '5ad996fe-134a-4625-a404-9d0cdae435d4',
    '68072fc9-3e84-4202-8e97-6c9c0c5fc83d',
    'c1c4d8f3-6cd5-439f-a546-943b5e2e8d8f',
    '479218ae-813b-4736-b3f2-7eec63640ffd',
    '90e22ace-ef5d-4cb5-a4a5-29fcd55ed660',
    '97d40306-fe6c-4911-8e68-1f9efc3d838f',
    'bd6fe2ce-b4ae-470e-8bdc-cf28a94c6208',
    '608349ff-5adf-4e1e-8cd7-7e0e41aee222',
    '241d094a-568f-4194-997c-fd08f67dcdac',
    '93b0a70d-c74e-4735-b70e-0c6e4c6a36ff',
    'e9f38ce3-5ed5-49f3-8713-c26de2eefd2b',
    'f263bc90-6307-462c-9e02-7b87d20e2840',
}

# this is the main record citation blueprint, use this in url_fors etc
blueprint = Blueprint(name='object', import_name=__name__, url_prefix='/object')
# this blueprint is here for the old citation urls, don't use it in url_fors etc
specimen_blueprint = Blueprint(
    name='specimen', import_name=__name__, url_prefix='/specimen'
)

# add to the default rdf content types to include json-ld as an alias for jsonld
rdf_content_types = {**CONTENT_TYPES, "json-ld": CONTENT_TYPES["jsonld"]}


def _context():
    return {
        'user': toolkit.c.user or toolkit.c.author,
        'auth_user_obj': toolkit.c.userobj,
    }


@specimen_blueprint.route('/<uuid>.<_format>', defaults={'version': None})
@specimen_blueprint.route('/<uuid>/<int:version>.<_format>')
@blueprint.route('/<uuid>.<_format>', defaults={'version': None})
@blueprint.route('/<uuid>/<int:version>.<_format>')
def rdf(uuid, _format, version):
    """
    Return RDF view of object.

    :param uuid: the object's uuid
    :param _format: the format requested
    :param version: the version of the record to retrieve, or None if the current version is desired
    :return: the data to display
    """
    data_dict = {
        'uuid': uuid,
        'format': _format,
        'version': version,
    }
    try:
        result = toolkit.get_action('object_rdf')(_context(), data_dict)
        return Response(result, mimetype=rdf_content_types[_format])
    except toolkit.ValidationError as e:
        toolkit.abort(409, str(e))


@specimen_blueprint.route('/<uuid>', defaults={'version': None})
@specimen_blueprint.route('/<uuid>/<int:version>')
@blueprint.route('/<uuid>', defaults={'version': None})
@blueprint.route('/<uuid>/<int:version>')
def view(uuid, version):
    """
    View object. If this is normal HTTP request, this will redirect to the record,
    otherwise if the request is for RDF (content negotiation) return the rdf.

    :param uuid: the uuid of the object
    :param version: the version of the object, or None for current version
    """
    if uuid in ABYSSLINE_UUIDS:
        abyssline_object_redirect(uuid, version)

    # is the request for a particular format?
    _format = check_access_header()

    if _format:
        # cetaf standards require us to return a 303 redirect to the rdf doc
        url = url_for('object.rdf', uuid=uuid, _format=_format, version=version)
        return redirect(url, code=303)
    else:
        try:
            # get the record at the given version
            record = get_record_by_uuid(uuid, version)
            if record:
                # cetaf standards require us to return a 303 redirect to the html record page
                return redirect(record.url(), code=303)
        except Exception:
            pass

    toolkit.abort(404, toolkit._('Record not found'))


def abyssline_object_redirect(uuid, version):
    """
    Temporary fix to allow abyssline object references to resolve to the temp dataset.

    :param uuid: the object's uuid
    :param version: the version to get
    """
    resource_id = toolkit.config.get('ckanext.nhm.abyssline_resource_id')

    # figure out the rounded version
    data_dict = {
        'resource_id': resource_id,
        'version': version,
    }
    version = toolkit.get_action('datastore_get_rounded_version')(_context(), data_dict)

    # search for the record
    search_data_dict = {'resource_id': resource_id, 'filters': {'catalogNumber': uuid}}

    search_result = toolkit.get_action('datastore_search')(_context(), search_data_dict)
    try:
        data = search_result['records'][0]
        record = Record(data['_id'], version, data, resource_id)
        redirect(record.url(), code=303)
    except IndexError:
        pass

    toolkit.abort(404, toolkit._('Record not found'))
