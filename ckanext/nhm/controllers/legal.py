
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class LegalController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """

    def privacy(self):
        return p.toolkit.render('legal/privacy.html', {'title': 'Privacy notice'})

    def terms(self):
        return p.toolkit.render('legal/terms.html', {'title': 'Terms and conditions'})