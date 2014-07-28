
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def citation(self):
        return p.toolkit.render('about/citation.html', {'title': 'Citation & attribution'})

    def download(self):
        return p.toolkit.render('about/download.html', {'title': 'Download & API'})

    def licensing(self):
        return p.toolkit.render('about/licensing.html', {'title': 'Data licensing'})

    def credits(self):
        return p.toolkit.render('about/credits.html', {'title': 'Credits'})

    def privacy(self):
        return p.toolkit.render('about/privacy.html', {'title': 'Privacy'})

    def terms(self):
        return p.toolkit.render('about/terms.html', {'title': 'Terms & conditions'})