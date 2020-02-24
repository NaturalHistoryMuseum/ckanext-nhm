# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

# bbcm = big butterfly count map :)
# create a flask blueprint
blueprint = Blueprint(name=u'big-butterfly-count-map', import_name=__name__)


@blueprint.route(u'/big-butterfly-count-map')
def bbcm():
    '''
    Render the big butterfly count map page.
    '''
    return toolkit.render(u'bbcm.html', {})
