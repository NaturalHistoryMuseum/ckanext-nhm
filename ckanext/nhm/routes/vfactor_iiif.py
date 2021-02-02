# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name='vfactor_iiif', import_name=__name__, url_prefix='/vfactor_iiif')


@blueprint.route('/')
def index():
    '''
    Render the vfactor iiif page.
    '''
    return toolkit.render('vfactor_iiif.html')
