# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(
    name='beetle-iiif', import_name=__name__, url_prefix='/beetle_iiif'
)


@blueprint.route('/')
def index():
    """
    Render the beetle iiif page.
    """
    return toolkit.render('beetle_iiif.html')
