# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name='legal', import_name=__name__)


@blueprint.route('/privacy')
def privacy():
    """
    Redirect to the Museum's privacy notice page.
    """
    return toolkit.redirect_to('https://www.nhm.ac.uk/about-us/privacy-notice.html')


@blueprint.route('/accessibility')
def a11y():
    """
    Redirect to the Museum's accessibility statement page.
    """
    return toolkit.redirect_to(
        'https://www.nhm.ac.uk/about-us/website-accessibility-statement.html'
    )


@blueprint.route('/terms-conditions')
def terms():
    """
    Render the terms and conditions page.
    """
    return toolkit.render('legal/terms.html', {'title': 'Terms and conditions'})


@blueprint.route('/harmful-content')
def aohc():
    """
    Render the Acknowledgement of harmful content statement page.
    """
    return toolkit.render(
        'legal/aohc.html', {'title': 'Acknowledgement of harmful content'}
    )


@blueprint.route('/understanding-the-collection')
def usc():
    """
    Redirect to the Museum's "Understanding and sharing the collection" page.
    """
    return toolkit.redirect_to(
        'https://www.nhm.ac.uk/about-us/governance/understanding-and-sharing-the-collection.html'
    )
