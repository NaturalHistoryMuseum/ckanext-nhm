# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

"""
Controller for displaying an individual record Loads all the data and then defers render
function to view objects.
"""

import json
import logging
from ckan.lib.helpers import link_to
from ckan.plugins import toolkit
from ckanext.nhm.lib.helpers import resource_view_get_view
from ckanext.nhm.lib.jinja_extensions import TaxonomyFormatExtension
from ckanext.nhm.lib.record import Record, RecordImage
from ckanext.nhm.views import DarwinCoreView
from flask import Blueprint, current_app, redirect

log = logging.getLogger(__name__)

blueprint = Blueprint(name='record', import_name=__name__)


def prepare_image(image: RecordImage) -> dict:
    """
    Given an image object, return a dict of information about it for the view.

    :param image: the RecordImage object
    :return: a dict of info
    """
    license_link = link_to(image.title, image.url, target='_blank')
    return {
        'title': image.title,
        'href': image.url,
        'download': image.download_url,
        'copyright': f'{license_link}<br /><small>{image.rights}</small>',
        'record_id': image.record.id,
        'resource_id': image.record.resource_id,
        'link': image.record.url(),
    }


def update_render_context(record: Record):
    """
    Sets the various expected context variables for the templates.

    The values set here are used in some of our templates and some core CKAN ones too,
    it's a bit of a mess (especially for packages).
    """
    toolkit.c.pkg_dict = toolkit.c.package = toolkit.c.pkg = record.package
    toolkit.c.resource = record.resource
    image_field = record.image_field
    # the templates expect for the record dict to not include the images
    toolkit.c.record_dict = {
        field: value for field, value in record.data.items() if field != image_field
    }
    toolkit.c.version = record.version
    toolkit.c.record_title = record.title
    toolkit.c.images = list(map(prepare_image, record.images))
    geojson = record.geojson
    # something expects this as json apparently, sigh
    toolkit.c.record_map = json.dumps(geojson) if geojson else None


@blueprint.before_app_first_request
def init_jinja_extensions():
    """
    This hook is called before the first request is received by the app and therefore
    allows us to ensure that the taxonomy extension is loaded into jinja2 before it's
    used.
    """
    # Load the taxonomy formatter
    current_app.jinja_env.add_extension(TaxonomyFormatExtension)


@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>.json',
    defaults={'version': None},
)
@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>.json/<int:version>'
)
def json_view(package_name, resource_id, record_id, version):
    """
    View the record as JSON.

    :param package_name: the package name or ID, we don't actually need this
    :param resource_id: the resource ID, we do need this!
    :param record_id: the record ID, stunningly enough we need this too
    :param version: optional record version, defaults to None which will be interpreted as now
    :return: the record data as a dict which will be turned into JSON automatically by Flask, huzzah
    """
    return Record(record_id, resource_id=resource_id, version=version).data


@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>',
    defaults={'version': None},
)
@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>/<int:version>'
)
def view(package_name, resource_id, record_id, version):
    """
    View an individual record.

    :param package_name: the package name or ID, doesn't matter which
    :param record_id: the record ID
    :param resource_id: the resource ID
    :param version: optional record version, defaults to None which will be interpreted as now
    :return: the rendered view template from the correct record view class
    """
    record = Record(
        record_id,
        package_id_or_name=package_name,
        resource_id=resource_id,
        version=version,
    )
    update_render_context(record)
    view_cls = resource_view_get_view(record.resource)
    return view_cls.render_record(toolkit.c)


@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>/dwc',
    defaults={'version': None},
)
@blueprint.route(
    '/dataset/<package_name>/resource/<resource_id>/record/<record_id>/dwc/<int:version>'
)
def dwc(package_name, resource_id, record_id, version):
    """
    View an individual record using the DwC view.

    :param package_name: the package name or ID, doesn't matter which
    :param record_id: the record ID
    :param resource_id: the resource ID
    :param version: optional record version, defaults to None which will be interpreted as now
    :return: the rendered view template from the correct record view class
    """
    record = Record(
        record_id,
        package_id_or_name=package_name,
        resource_id=resource_id,
        version=version,
    )
    update_render_context(record)
    toolkit.c.additional_view = True
    return DarwinCoreView().render_record(toolkit.c)


@blueprint.route('/record/<resource_id>/<record_id>', defaults={'version': None})
@blueprint.route('/record/<resource_id>/<record_id>/<int:version>')
def permalink(resource_id, record_id, version):
    resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
    if not resource:
        raise toolkit.Invalid
    url = toolkit.url_for(
        'record.view',
        package_name=resource['package_id'],
        resource_id=resource_id,
        record_id=record_id,
        version=version,
    )
    return redirect(url)
