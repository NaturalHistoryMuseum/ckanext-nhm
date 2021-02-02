# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

'''
Controller for displaying an individual record
Loads all the data and then defers render function to view objects
'''

import json
import logging

from ckan import model
from ckan.plugins import toolkit
from flask import Blueprint, current_app

from ckanext.nhm.lib.helpers import resource_view_get_view
from ckanext.nhm.lib.jinja_extensions import TaxonomyFormatExtension
from ckanext.nhm.views import DarwinCoreView

log = logging.getLogger(__name__)

blueprint = Blueprint(name='record', import_name=__name__, url_prefix='/dataset')


def _load_data(package_name, resource_id, record_id, version=None):
    '''Load the data for dataset, resource and record (into toolkit.c variable).

    :param package_name:
    :param record_id:
    :param resource_id:

    '''
    context = {
        'user': toolkit.c.user or toolkit.c.author
    }

    # try & get the resource
    try:
        toolkit.c.resource = toolkit.get_action('resource_show')(context, {
            'id': resource_id
        })
        toolkit.c.package = toolkit.get_action('package_show')(context, {
            'id': package_name
        })
        # required for nav menu
        toolkit.c.pkg = context['package']
        toolkit.c.pkg_dict = toolkit.c.package

        record_data_dict = {
            'resource_id': resource_id,
            'record_id': record_id
        }
        if version is not None:
            version = int(version)
            record_data_dict['version'] = version
        toolkit.c.version = version
        record = toolkit.get_action('record_show')(context, record_data_dict)
        toolkit.c.record_dict = record['data']

    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._('Resource not found'))
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._(f'Unauthorized to read resource {package_name}'))

    field_names = {
        'image': toolkit.c.resource.get('_image_field', None),
        'title': toolkit.c.resource.get('_title_field', None),
        'latitude': toolkit.c.resource.get('_latitude_field', None),
        'longitude': toolkit.c.resource.get('_longitude_field', None),
    }

    # if this is a DwC dataset, add some default for image and lat/lon fields
    if toolkit.c.resource['format'].lower() == 'dwc':
        for field_name, dwc_field in [('latitude', 'decimalLatitude'),
                                      ('longitude', 'decimalLongitude')]:
            if dwc_field in toolkit.c.record_dict:
                field_names[field_name] = dwc_field

    # assign title based on the title field
    toolkit.c.record_title = toolkit.c.record_dict.get(field_names['title'],
                                                       f'Record {toolkit.c.record_dict.get("_id")}')

    # sanity check: image field hasn't been set to _id
    if field_names['image'] and field_names['image'] != '_id':
        default_copyright = '<small>&copy; The Trustees of the Natural History ' \
                            'Museum, London</small>'
        licence_id = toolkit.c.resource.get('_image_licence') or 'cc-by'
        short_licence_id = licence_id[:5].lower()
        # try and overwrite default licence with more specific one
        for l_id in [licence_id, short_licence_id]:
            try:
                licence = model.Package.get_license_register()[l_id]
                break
            except KeyError:
                continue

        licence_url = toolkit.h.link_to(licence.title, licence.url, target="_blank")
        default_licence = f'Licence: {licence_url}'

        # pop the image field so it isn't output as part of the
        # record_dict/field_data dict (see self.view())
        image_field_value = toolkit.c.record_dict.pop(field_names['image'], None)

        if image_field_value:
            # init the images list on the context var
            toolkit.c.images = []

            if isinstance(image_field_value, list):
                for image in image_field_value:
                    href = image.get('identifier', None)
                    if href:
                        license_link = toolkit.h.link_to(image.get('license'),
                                                         image.get(
                                                             'license')) if image.get(
                            'license', None) else None
                        toolkit.c.images.append({
                            'title': image.get('title', None) or toolkit.c.record_title,
                            'href': href,
                            'copyright': f'{license_link or default_licence}<br />'
                                         f'{image.get("rightsHolder", None) or default_copyright}',
                            'record_id': record_id,
                            'resource_id': resource_id,
                            'link': toolkit.url_for(
                                controller='ckanext.nhm.controllers.record:RecordController',
                                action='view',
                                package_name=package_name,
                                resource_id=resource_id,
                                record_id=record_id
                            ),
                        })
            else:
                # it's a string field value, use the delimiter to split up the field
                # value (if there is one!)
                delimiter = toolkit.c.resource.get('_image_delimiter', None)
                if delimiter:
                    images = image_field_value.split(delimiter)
                else:
                    images = [image_field_value]
                # loop through the images, adding dicts with their details to the context
                for image in images:
                    if image.strip():
                        toolkit.c.images.append({
                            'title': toolkit.c.record_title,
                            'href': image.strip(),
                            'copyright': f'{default_licence}<br />{default_copyright}'
                        })

    if field_names['latitude'] and field_names['longitude']:
        latitude = toolkit.c.record_dict.get(field_names['latitude'])
        longitude = toolkit.c.record_dict.get(field_names['longitude'])

        if latitude and longitude:
            # create a piece of GeoJSON to point at the specific record location on a map
            toolkit.c.record_map = json.dumps({
                'type': 'Point',
                'coordinates': [float(longitude), float(latitude)]
            })


@blueprint.before_app_first_request
def init_jinja_extensions():
    '''
    This hook is called before the first request is received by the app and therefore allows us to
    ensure that the taxonomy extension is loaded into jinja2 before it's used.
    '''
    # Load the taxonomy formatter
    current_app.jinja_env.add_extension(TaxonomyFormatExtension)


@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>',
                 defaults={'version': None})
@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>/<int:version>')
def view(package_name, resource_id, record_id, version):
    '''View an individual record.

    :param package_name:
    :param record_id:
    :param resource_id:
    :param version:

    '''
    _load_data(package_name, resource_id, record_id, version)
    view_cls = resource_view_get_view(toolkit.c.resource)
    return view_cls.render_record(toolkit.c)


@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>/dwc',
                 defaults={'version': None})
@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>/dwc/<int:version>')
def dwc(package_name, resource_id, record_id, version):
    '''Explicit DwC view

    :param package_name:
    :param record_id:
    :param resource_id:
    :param version:

    '''
    _load_data(package_name, resource_id, record_id, version)

    # Is this a DwC view of an additional dataset?
    # In which case, provide links back to the original record view
    toolkit.c.additional_view = True

    return DarwinCoreView().render_record(toolkit.c)
