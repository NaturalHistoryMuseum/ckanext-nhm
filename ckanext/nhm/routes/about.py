# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint

# create a flask blueprint with a prefix
blueprint = Blueprint(name='about', import_name=__name__, url_prefix='/about')


@blueprint.route('/citation')
def citation():
    """
    Render the "about" page for citations and attributions.
    """
    return toolkit.render('about/citation.html', {'title': 'Citation and attribution'})


@blueprint.route('/download')
def download():
    """
    Render the "about" page for downloads and the API.
    """
    return toolkit.render('about/download.html', {'title': 'Download and API'})


@blueprint.route('/credits')
def credits():
    """
    Render the "about" page for credits.
    """
    return toolkit.render('about/credits.html', {'title': 'Credits'})


@blueprint.route('/privacy')
def privacy():
    """
    Render the "about" page for privacy.
    """
    return toolkit.render('about/privacy.html', {'title': 'Privacy'})


@blueprint.route('/terms')
def terms():
    """
    Render the "about" page for terms and conditions.
    """
    return toolkit.render('about/terms.html', {'title': 'Terms and conditions'})


@blueprint.route('/datacite')
def datacite():
    """
    Render the "about" page for DataCite service provider.
    """
    return toolkit.render('about/datacite.html', {'title': 'DataCite Service Provider'})


@blueprint.route('/harmful-content')
def aohc():
    """
    Render the Acknowledgement of harmful content statement page.
    """
    return toolkit.render(
        'about/aohc.html', {'title': 'Acknowledgement of harmful content'}
    )
