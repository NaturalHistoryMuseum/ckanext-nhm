# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

# create a flask blueprint with a prefix
blueprint = Blueprint(name=u'about', import_name=__name__, url_prefix=u'/about')


@blueprint.route('/citation')
def citation():
    '''Render the "about" page for citations and attributions.'''
    return toolkit.render(u'about/citation.html',
                          {
                              u'title': u'Citation and attribution'
                              })


@blueprint.route('/download')
def download():
    '''Render the "about" page for downloads and the API.'''
    return toolkit.render(u'about/download.html', {
        u'title': u'Download and API'
        })


@blueprint.route('/credits')
def credits():
    '''Render the "about" page for credits.'''
    return toolkit.render(u'about/credits.html', {
        u'title': u'Credits'
        })


@blueprint.route('/privacy')
def privacy():
    '''Render the "about" page for privacy.'''
    return toolkit.render(u'about/privacy.html', {
        u'title': u'Privacy'
        })


@blueprint.route('/terms')
def terms():
    '''Render the "about" page for terms and conditions.'''
    return toolkit.render(u'about/terms.html', {
        u'title': u'Terms and conditions'
        })
