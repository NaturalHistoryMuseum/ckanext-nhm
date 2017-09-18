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
from ckanext.nhm.lib.helpers import get_contributor_count
import ckan.lib.helpers as h
import ckanext.stats.stats as stats_lib
from datetime import datetime, timedelta, date
from ckan.model import TrackingSummary, Resource
from sqlalchemy import and_
from pylons import config
from sqlalchemy import func
from dateutil import rrule

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

    def resources(self):

        # Get the oldest tracking date
        oldest_created_date = model.Session.query(
            Resource.created,
        ).order_by(Resource.created).limit(1).scalar()

        # If oldest date is none (no stats yet) we don't want to continue
        if oldest_created_date:
            # Calc difference between dates

            delta = datetime.now() - oldest_created_date

        # If we have data for more than 31 days, we'll show by month; otherwise segment by da
        if delta.days > 10:
            c.date_interval = 'month'
            label_formatter = '%b %Y'
        else:
            c.date_interval = 'day'
            label_formatter = '%d/%m/%y'

        date_func = func.date_trunc(c.date_interval, Resource.created)

        q = model.Session.query(
            date_func.label('date'),
            func.count().label('count')
        )

        q = q.order_by(date_func)
        q = q.group_by(date_func)

        c.graph_options = {
            'series': {
                'lines': {'show': True},
                'points': {'show': True}
            },
            'xaxis': {
                'mode': 'time',
                'ticks': []
            },
            'yaxis': {
                'tickDecimals': 0
            }
        }

        c.graph_data = []
        total = 0

        for i, stat in enumerate(q.all()):
            total += stat.count
            c.graph_data.append([i, total])

            formatted_date = stat.date.strftime(label_formatter)
            c.graph_options['xaxis']['ticks'].append([i, formatted_date])

        return p.toolkit.render('stats/resources.html', {'title': 'Resource statistics'})

    def contributors(self):

        # Get number of contributors
        c.contributors = model.Session.execute(
            "SELECT u.id AS user_id, u.name, u.fullname, COUNT(p.id) AS count FROM package p INNER JOIN public.user u ON u.id = p.creator_user_id WHERE u.state='active' AND p.state='active' GROUP BY u.id ORDER BY count DESC").fetchall()

        contributor_count = get_contributor_count()

        c.num_contributors = [
            {'date': datetime.now() - timedelta(days=7), 'count': 0},
            {'date': datetime.now(), 'count': contributor_count},
        ]

        return p.toolkit.render('stats/contributors.html', {'title': 'Contributor statistics'})

    def records(self):

        c.datastore_stats = get_action('dataset_stats')(self.context, {})
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

        # If this is a new dataset, and we only have recent tracking metrics
        # We want to show stats per day, rather than per month

        # Get the oldest tracking date
        oldest_date = model.Session.query(
            TrackingSummary.tracking_date,
        ).filter(TrackingSummary.package_id == c.pkg_dict['id']).order_by(TrackingSummary.tracking_date).limit(1).scalar()

        # If oldest date is none (no stats yet) we don't want to continue
        if oldest_date:
            # Calc difference between dates
            delta = date.today() - oldest_date

            # If we have data for more than 31 days, we'll show by month; otherwise segment by da
            if delta.days > 10:
                c.date_interval = 'month'
                label_formatter = '%b %Y'
                rrule_interval = rrule.MONTHLY
            else:
                c.date_interval = 'day'
                label_formatter = '%d/%m/%y'
                rrule_interval = rrule.DAILY

            date_func = func.date_trunc(c.date_interval, TrackingSummary.tracking_date)

            q = model.Session.query(
                date_func.label('date'),
                func.sum(TrackingSummary.count).label('sum')
            )

            q = q.filter(and_(TrackingSummary.package_id == c.pkg_dict['id']))
            q = q.order_by(date_func)
            q = q.group_by(date_func)

            tracking_stats = {}

            # Create a dictionary of tracking stat results
            for stat in q.all():
                # Keyed by formatted date
                formatted_date = stat.date.strftime(label_formatter)
                tracking_stats[formatted_date] = int(stat.sum)

            # https://github.com/joetsoi/flot-barnumbers
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
                    'lineWidth': 0.7,
                    'barWidth': 0.9,
                    'showNumbers': 1,
                    'numbers': {
                        'xAlign': 1,
                        'yAlign': 1,
                        'top': -15  # BS: Added this. Need to patch flot.barnumbers properly
                    }
                }
            }

            for i, dt in enumerate(rrule.rrule(rrule_interval, dtstart=oldest_date, until=date.today())):

                formatted_date = dt.strftime(label_formatter)

                # Do we have a value from the tracking stats?
                try:
                    count = tracking_stats[formatted_date]
                except KeyError:
                    # No value - count is zero
                    count = 0

                # Add data
                c.pageviews.append([i, count])

                # Add date label to ticks
                c.pageviews_options['xaxis']['ticks'].append([i, formatted_date])

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

        # FIXME: This does not work!!

        for resource in c.pkg_dict['resources']:

            params = {
                'secret': config.get("ckanpackager.secret"),
                'resource_id': resource['id']
            }

            try:
                r = requests.post(endpoint, params)
                result = r.json()
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
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
