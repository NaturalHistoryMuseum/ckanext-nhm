#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


class AboutController(toolkit.BaseController):
    '''Controller for displaying "about" pages.'''

    def citation(self):
        '''Render the "about" page for citations and attributions.'''
        return toolkit.render(u'about/citation.html',
                              {u'title': u'Citation and attribution'})

    def download(self):
        '''Render the "about" page for downloads and the API.'''
        return toolkit.render(u'about/download.html', {u'title': u'Download and API'})

    def credits(self):
        '''Render the "about" page for credits.'''
        return toolkit.render(u'about/credits.html', {u'title': u'Credits'})

    def privacy(self):
        '''Render the "about" page for privacy.'''
        return toolkit.render(u'about/privacy.html', {u'title': u'Privacy'})

    def terms(self):
        '''Render the "about" page for terms and conditions.'''
        return toolkit.render(u'about/terms.html', {u'title': u'Terms and conditions'})
