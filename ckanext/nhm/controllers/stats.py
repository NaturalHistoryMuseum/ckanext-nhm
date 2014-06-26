
import ckan.plugins as p
from ckan.common import _, g, c
from collections import OrderedDict
import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
from ckanext.nhm.lib.helpers import get_datastore_stats, get_contributor_count
import ckan.lib.helpers as h
import ckanext.stats.stats as stats_lib
from datetime import datetime, timedelta
from ckanext.ga_report.ga_model import GA_Url, GA_Publisher
from sqlalchemy import and_

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action
check_access = logic.check_access

class StatsController(p.toolkit.BaseController):
    """
    Controller for displaying stats pages
    """

    def __before__(self, action, **env):

        base.BaseController.__before__(self, action, **env)

        try:
            self.context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}
            # check_access('site_read', self.context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

    def datasets(self):

        stats = stats_lib.Stats()
        rev_stats = stats_lib.RevisionStats()

        c.num_packages_by_week = rev_stats.get_num_packages_by_week()

        # Used in new CKAN templates gives more control to the templates for formatting.
        c.raw_packages_by_week = []
        for week_date, num_packages, cumulative_num_packages in c.num_packages_by_week:
            c.raw_packages_by_week.append({'date': h.date_str_to_datetime(week_date), 'total_packages': cumulative_num_packages})

        return p.toolkit.render('stats/datasets.html', {'title': 'Dataset statistics'})

    def contributors(self):

        # Get number of contributors
        c.contributors = model.Session.execute("SELECT u.id AS user_id, u.name, u.fullname, COUNT(p.id) as count FROM package p INNER JOIN public.user u ON u.id = p.creator_user_id WHERE u.state='active' and p.state='active' GROUP BY u.id ORDER BY count DESC").fetchall()

        contributor_count = get_contributor_count()

        c.num_contributors = [
            {'date': datetime.now() - timedelta(days=7), 'count': 0},
            {'date': datetime.now(), 'count': contributor_count},
        ]

        return p.toolkit.render('stats/contributors.html', {'title': 'Contributor statistics'})

    def records(self):

        c.datastore_stats = get_datastore_stats()

        c.num_records = [
            {'date': datetime.now() - timedelta(days=7), 'count': 0},
            {'date': datetime.now(), 'count': c.datastore_stats['total']},
        ]

        return p.toolkit.render('stats/records.html', {'title': 'Record statistics'})

    def dataset_metrics(self, id):

        data_dict = {'id': id}

        # check if package exists
        try:
            c.pkg_dict = get_action('package_show')(self.context, data_dict)
            c.pkg = self.context['package']
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)

        urls = model.Session.query(GA_Url).filter(and_(GA_Url.package_id == c.pkg_dict['name'], GA_Url.period_name != 'All')).order_by(GA_Url.period_name.asc()).all()

        c.pageviews = OrderedDict()
        c.total_pageviews = 0

        c.pageviews['2014-05'] = 0

        for url in urls:
                c.pageviews[url.period_name] = url.pageviews
                c.total_pageviews += int(url.pageviews)

        return render('stats/dataset_metrics.html')

