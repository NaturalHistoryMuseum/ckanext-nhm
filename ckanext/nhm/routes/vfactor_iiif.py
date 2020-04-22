# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name=u'vfactor_iiif', import_name=__name__, url_prefix=u'/viiif')


@blueprint.route(u'/')
def index():
    '''
    Render the vfactor iiif page.
    '''
    return toolkit.render(u'vfactor_iiif.html')
