# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

# create a flask blueprint with a prefix
blueprint = Blueprint(name=u'help', import_name=__name__, url_prefix=u'/help')


@blueprint.route('/')
@blueprint.route('')
def index():
    '''Render the help index.'''
    return toolkit.render(u'help/index.html', {
        u'title': u'Help'
        })


@blueprint.route('/search')
def search():
    '''Render the help page for integrated search.'''
    return toolkit.render(u'help/search.html', {
        u'title': u'Integrated Search Help'
        })
