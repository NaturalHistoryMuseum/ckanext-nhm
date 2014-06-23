
import ckan.plugins as p
from ckan.common import _, g, c


class PageController(p.toolkit.BaseController):
    """
    Controller for displaying static pages
    """
    def about_data_usage(self):
        return p.toolkit.render('about/data_usage.html', {'title': 'Guidelines for data use'})

    def about_credits(self):
        return p.toolkit.render('about/credits.html', {'title': 'Credits'})