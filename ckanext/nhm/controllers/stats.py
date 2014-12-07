
import os
import ckan.plugins as p
from ckan.common import _, g, c
from collections import OrderedDict
import requests
from requests import ConnectionError
import logging
import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
from ckanext.nhm.lib.helpers import get_datastore_stats, get_contributor_count
import ckan.lib.helpers as h
import ckanext.stats.stats as stats_lib
from datetime import datetime, timedelta
from ckan.model import TrackingSummary
from sqlalchemy import and_
from pylons import config
from sqlalchemy import func

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action
check_access = logic.check_access

log = logging.getLogger(__name__)

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

        date_func = func.date_trunc('month', TrackingSummary.tracking_date)

        q = model.Session.query(
            date_func.label('date'),
            func.sum(TrackingSummary.count).label('sum')
        )

        q = q.filter(and_(TrackingSummary.package_id == c.pkg_dict['id']))
        q = q.order_by(date_func)
        q = q.group_by(date_func)

        stats = q.all()

        c.pageviews = []
        c.pageviews_options = {
            'grid': {
                'borderWidth': {'top': 0, 'right': 0, 'bottom': 1, 'left': 1},
                'borderColor': "#D4D4D4"
            },
            'xaxis': {
                'ticks': [],
                'tickLength': 0
            },
            'yaxis': {
                'tickLength': 0
            },
            'bars': {
                'show': 1,
                'align': "center",
                'zero': 1,
                'fill': 1,
                'fillColor': '#D7EDFD',
                'lineWidth': 0,
                'barWidth': 0.99,
                'showNumbers': 1,
                'numbers': {
                    'xAlign': 1,
                    'yAlign': 1
                }
            }
        }

        # https://github.com/joetsoi/flot-barnumbers
        for i, stat in enumerate(stats):

            # Add the data
            c.pageviews.append([i, int(stat.sum)])

            #  Convert the period name into something a bit nicer: 2014-11 => Nov 2014
            label = stat.date.strftime('%b %Y')

            # label = str(stat.date)
            c.pageviews_options['xaxis']['ticks'].append([i, label])

        # Try and get resource download metrics - these are per resource
        # So need to loop through all resources, looking up download stats
        # Post to /dataset with secret and resource_id, and receive back:
        #   {
        #    "status": "success",
        #    "totals": {
        #        "..the resource id you specified...": {
        #            "emails": 2,
        #            "errors": 0,
        #            "requests": 2
        #        }
        #    }
        # }

        c.resource_downloads = []
        c.total_downloads = 0

        endpoint = os.path.join(config.get("ckanpackager.url"), 'statistics')

        for resource in c.pkg_dict['resources']:

            params = {
                'secret': config.get("ckanpackager.secret"),
                'resource_id': resource['id']
            }

            try:
                r = requests.post(endpoint, params)
                result = r.json()
            except ValueError:   # includes simplejson.decoder.JSONDecodeError
                # Unable to retrieve download stats for this resource
                log.critical('ERROR %s: Unable to retrieve download stats for resource %s', r.status_code, resource['id'])
            except ConnectionError, e:
                log.critical(e)
            else:
                try:
                    total = int(result['totals'][resource['id']]['emails'])
                except KeyError:
                    # We do not have stats for this resource
                    pass
                else:
                    c.resource_downloads.append(
                        {
                            'name': resource['name'],
                            'id': resource['id'],
                            'total': total
                         }
                    )

                    c.total_downloads += total

        return render('stats/dataset_metrics.html')