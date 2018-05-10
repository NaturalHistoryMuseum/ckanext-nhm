
import ckan.plugins as p


class LegalController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """

    def privacy(self):
        # redirect to the Museum's main privacy page
        p.toolkit.redirect_to('http://www.nhm.ac.uk/about-us/privacy-notice.html')

    def terms(self):
        return p.toolkit.render('legal/terms.html', {'title': 'Terms and conditions'})
