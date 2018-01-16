#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


class LegalController(toolkit.BaseController):
    '''Controller for displaying legal pages'''

    def privacy(self):
        '''Render the privacy notice page.'''
        return toolkit.render(u'legal/privacy.html', {u'title': u'Privacy notice'})

    def terms(self):
        '''Render the terms and conditions page.'''
        return toolkit.render(u'legal/terms.html', {u'title': u'Terms and conditions'})
