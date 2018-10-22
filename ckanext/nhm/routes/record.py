# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json
import logging

from ckanext.nhm.lib.helpers import resource_view_get_view
from ckanext.nhm.lib.jinja_extensions import TaxonomyFormatExtension
from ckanext.nhm.views import DarwinCoreView

import ckan.model as model

# from ckanext.nhm.views import DarwinCoreView

log = logging.getLogger(__name__)

TILED_MAP_TYPE = u'tiledmap'
from flask import Blueprint

from ckan.plugins import toolkit

blueprint = Blueprint(name=u'record', import_name=__name__, url_prefix=u'/dataset')


def _load_data(package_name, resource_id, record_id):
    '''Load the data for dataset, resource and record (into toolkit.c variable).

    :param package_name:
    :param record_id:
    :param resource_id:

    '''
    context = {
        u'user': toolkit.c.user or toolkit.c.author
        }

    # Try & get the resource
    try:
        toolkit.c.resource = toolkit.get_action(u'resource_show')(context, {
            u'id': resource_id
            })
        toolkit.c.package = toolkit.get_action(u'package_show')(context, {
            u'id': package_name
            })
        # required for nav menu
        toolkit.c.pkg = context[u'package']
        toolkit.c.pkg_dict = toolkit.c.package
        record = toolkit.get_action(u'record_show')(context, {
            u'resource_id': resource_id,
            u'record_id': record_id
            })
        toolkit.c.record_dict = record[u'data']
        record_field_types = {f[u'id']: f[u'type'] for f in record[u'fields']}

    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._(u'Resource not found'))
    except toolkit.NotAuthorized:
        toolkit.abort(401,
                      toolkit._(u'Unauthorized to read resource %s') % package_name)

    field_names = {
        u'image': toolkit.c.resource.get(u'_image_field', None),
        u'title': toolkit.c.resource.get(u'_title_field', None),
        u'latitude': None,
        u'longitude': None
        }

    # Get lat/long fields
    # Loop through all the views - if we have a tiled map view with lat/lon fields
    # We'll use those fields to add the map
    views = toolkit.get_action(u'resource_view_list')(context,
                                                      {
                                                          u'id': resource_id
                                                          })
    for view in views:
        if view[u'view_type'] == TILED_MAP_TYPE:
            field_names[u'latitude'] = view[u'latitude_field']
            field_names[u'longitude'] = view[u'longitude_field']
            break

    # If this is a DwC dataset, add some default for image and lat/lon fields
    if toolkit.c.resource[u'format'].lower() == u'dwc':
        for field_name, dwc_field in [(u'latitude', u'decimalLatitude'),
                                      (u'longitude', u'decimalLongitude')]:
            if dwc_field in toolkit.c.record_dict:
                field_names[field_name] = dwc_field

    # Assign title based on the title field
    toolkit.c.record_title = toolkit.c.record_dict.get(field_names[u'title'],
                                                       u'Record %s' %
                                                       toolkit.c.record_dict.get(
                                                           u'_id'))

    # Sanity check: image field hasn't been set to _id
    if field_names[u'image'] and field_names[u'image'] != u'_id':
        default_copyright = u'<small>&copy; The Trustees of the Natural History ' \
                            u'Museum, London</small>'
        licence_id = toolkit.c.resource.get(u'_image_licence') or u'cc-by'
        short_licence_id = licence_id[:5].lower()
        # try and overwrite default licence with more specific one
        for l_id in [licence_id, short_licence_id]:
            try:
                licence = model.Package.get_license_register()[l_id]
                break
            except KeyError:
                continue

        default_licence = u'Licence: %s' % toolkit.h.link_to(licence.title,
                                                             licence.url,
                                                             target=u'_blank')

        # pop the image field so it isn't output as part of the
        # record_dict/field_data dict (see self.view())
        image_field_value = toolkit.c.record_dict.pop(field_names[u'image'], None)

        if image_field_value:
            # init the images list on the context var
            toolkit.c.images = []

            # try and convert image to json
            try:
                images = json.loads(image_field_value)
            except ValueError:
                # if it fails, it's a string field value
                # use the delimiter to split up the field value (if there is one!)
                delimiter = toolkit.c.resource.get(u'_image_delimiter', None)
                if delimiter:
                    images = image_field_value.split(delimiter)
                else:
                    images = [image_field_value]
                # loop through the images, adding dicts with their details to the
                # context
                for image in images:
                    if image.strip():
                        toolkit.c.images.append({
                            u'title': toolkit.c.record_title,
                            u'href': image.strip(),
                            u'copyright': u'%s<br />%s' % (
                                default_licence, default_copyright)
                            })
            else:
                for image in images:
                    href = image.get(u'identifier', None)
                    if href:
                        license_link = toolkit.h.link_to(image.get(u'license'),
                                                         image.get(
                                                             u'license')) if \
                            image.get(
                                u'license', None) else None
                        toolkit.c.images.append({
                            u'title': image.get(u'title',
                                                None) or toolkit.c.record_title,
                            u'href': href,
                            u'copyright': u'%s<br />%s' % (
                                license_link or default_licence,
                                image.get(u'rightsHolder',
                                          None) or default_copyright),
                            u'record_id': record_id,
                            u'resource_id': resource_id,
                            u'link': toolkit.url_for(u'record.view',
                                package_name=package_name,
                                resource_id=resource_id,
                                record_id=record_id
                                ),
                            })

    if field_names[u'latitude'] and field_names[u'longitude']:
        latitude, longitude = toolkit.c.record_dict.get(
            field_names[u'latitude']), toolkit.c.record_dict.get(
            field_names[u'longitude'])

        if latitude and longitude:
            toolkit.c.record_map = json.dumps({
                u'type': u'Point',
                u'coordinates': [longitude, latitude]
                })


@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>')
def view(package_name, resource_id, record_id):
    '''View an individual record.

    :param package_name:
    :param record_id:
    :param resource_id:

    '''
    _load_data(package_name, resource_id, record_id)

    view_cls = resource_view_get_view(toolkit.c.resource)

    # Load the taxonomy formatter
    toolkit.c.pylons.app_globals.jinja_env.add_extension(TaxonomyFormatExtension)

    return view_cls.render_record(toolkit.c)


@blueprint.route('/<package_name>/resource/<resource_id>/record/<record_id>/dwc')
def dwc(package_name, resource_id, record_id):
    '''Explicit DwC view

    :param package_name:
    :param record_id:
    :param resource_id:

    '''

    _load_data(package_name, resource_id, record_id)

    # Is this a DwC view of an additional dataset?
    # In which case, provide links back to the original record view
    toolkit.c.additional_view = True

    view = DarwinCoreView()
    return view.render_record(toolkit.c)
