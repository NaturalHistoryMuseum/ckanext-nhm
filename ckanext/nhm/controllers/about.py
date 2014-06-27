
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def data_usage(self):
        return p.toolkit.render('about/data_usage.html', {'title': 'Guidelines for data use'})

    def credits(self):
        return p.toolkit.render('about/credits.html', {'title': 'Credits'})