# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

# bbcm = big butterfly count map :)
# create a flask blueprint with a prefix
blueprint = Blueprint(name=u'big-butterfly-count-map', import_name=__name__,
                      url_prefix=u'/big-butterfly-count-map')


@blueprint.route(u'')
@blueprint.route(u'/')
def bbcm():
    '''
    Render the big butterfly count map page.
    '''
    return toolkit.render(u'bbcm.html', {})
