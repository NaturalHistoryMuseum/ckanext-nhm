
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class PageController(p.toolkit.BaseController):
    """
    Controller for displaying static pages
    """
    def about_data_usage(self):
        return p.toolkit.render('about/data_usage.html', {'title': 'Guidelines for data use'})

    def about_credits(self):
        return p.toolkit.render('about/credits.html', {'title': 'Credits'})

    def about_statistics(self):

        # ALl of these are taken from the stats module
        # We're re-writing it as we don't want all their content, and they haven't made it easy to override
        stats = stats_lib.Stats()

        rev_stats = stats_lib.RevisionStats()

        c.num_packages_by_week = rev_stats.get_num_packages_by_week()
        c.package_revisions_by_week = rev_stats.get_by_week('package_revisions')
        c.new_packages_by_week = rev_stats.get_by_week('new_packages')

        c.raw_packages_by_week = []
        for week_date, num_packages, cumulative_num_packages in c.num_packages_by_week:
            c.raw_packages_by_week.append({'date': h.date_str_to_datetime(week_date), 'total_packages': cumulative_num_packages})

        c.raw_all_package_revisions = []
        for week_date, revs, num_revisions, cumulative_num_revisions in c.package_revisions_by_week:
            c.raw_all_package_revisions.append({'date': h.date_str_to_datetime(week_date), 'total_revisions': num_revisions})

        c.raw_new_datasets = []
        for week_date, pkgs, num_packages, cumulative_num_packages in c.new_packages_by_week:
            c.raw_new_datasets.append({'date': h.date_str_to_datetime(week_date), 'new_packages': num_packages})

        return p.toolkit.render('about/statistics.html', {'title': 'Statistics'})


