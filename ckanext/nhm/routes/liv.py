# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name='liv', import_name=__name__, url_prefix='/image-viewer')


@blueprint.route('/')
@blueprint.route('/<mode>')
@blueprint.route('/<mode>/<path:mode_params>')
def index(mode='', mode_params=''):
    """
    Render the image viewer page.
    """
    # the template doesn't actually do anything with the args but we may as well pass
    # them in anyway
    return toolkit.render(
        'liv.html', extra_vars={'mode': mode, 'mode_params': mode_params}
    )
