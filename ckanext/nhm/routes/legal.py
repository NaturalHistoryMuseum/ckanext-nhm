# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from flask import Blueprint

from ckan.plugins import toolkit

blueprint = Blueprint(name=u'legal', import_name=__name__)


@blueprint.route('/privacy')
def privacy():
    '''Redirect to the museum's privacy notice page.'''
    return toolkit.redirect_to(u'http://www.nhm.ac.uk/about-us/privacy-notice.html')


@blueprint.route('/terms-conditions')
def terms():
    '''Render the terms and conditions page.'''
    return toolkit.render(u'legal/terms.html', {
        u'title': u'Terms and conditions'
        })
