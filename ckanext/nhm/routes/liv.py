# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name='liv', import_name=__name__, url_prefix='/image-viewer')


@blueprint.route('/')
@blueprint.route('/<path:mode>')
def index(mode=''):
    """
    Render the image viewer page.
    """
    return toolkit.render('liv.html', extra_vars={'mode': mode})
