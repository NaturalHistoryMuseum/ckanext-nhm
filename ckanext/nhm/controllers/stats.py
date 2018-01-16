#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from datetime import date, datetime, timedelta

import os
import requests
from ckanext.nhm.lib.helpers import get_contributor_count
from dateutil import rrule
from pylons import config
from requests import ConnectionError
from sqlalchemy import and_, func

import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


class StatsController(toolkit.BaseController):
    '''Controller for displaying stats pages.'''

    def __before__(self, action, **env):
        toolkit.BaseController.__before__(self, action, **env)

        try:
            self.context = {
                u'user': toolkit.c.user or toolkit.c.author,
                u'auth_user_obj': toolkit.c.userobj
                }  # check_access('site_read', self.context)
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._(u'Not authorized to see this page'))

    def resources(self):
        '''Render the resources statistics page.'''

        # Get the oldest tracking date
        oldest_created_date = model.Session.query(model.Resource.created, ).order_by(
                model.Resource.created).limit(1).scalar()

        # If oldest date is none (no stats yet) we don't want to continue
        if oldest_created_date:
            # Calc difference between dates

            delta = datetime.now() - oldest_created_date

        # If we have data for more than 31 days, we'll show by month;
        # otherwise segment by day
        if delta.days > 10:
            toolkit.c.date_interval = u'month'
            label_formatter = u'%b %Y'
        else:
            toolkit.c.date_interval = u'day'
            label_formatter = u'%d/%m/%y'

        date_func = func.date_trunc(toolkit.c.date_interval, model.Resource.created)

        q = model.Session.query(date_func.label(u'date'), func.count().label(u'count'))

        q = q.order_by(date_func)
        q = q.group_by(date_func)

        toolkit.c.graph_options = {
            u'series': {
                u'lines': {u'show': True}, u'points': {u'show': True}
                }, u'xaxis': {
                u'mode': u'time', u'ticks': []
                }, u'yaxis': {
                u'tickDecimals': 0
                }
            }

        toolkit.c.graph_data = []
        total = 0

        for i, stat in enumerate(q.all()):
            total += stat.count
            toolkit.c.graph_data.append([i, total])

            formatted_date = stat.date.strftime(label_formatter)
            toolkit.c.graph_options[u'xaxis'][u'ticks'].append([i, formatted_date])

        return toolkit.render(u'stats/resources.html',
                              {u'title': u'Resource statistics'})

    def contributors(self):
        '''Render the contributor stats page.'''

        # Get number of contributors
        toolkit.c.contributors = model.Session.execute(
                u"SELECT u.id AS user_id, u.name, u.fullname, COUNT(p.id) AS count "
                u"FROM package p INNER JOIN public.user u ON u.id = p.creator_user_id "
                u"WHERE u.state='active' AND p.state='active' "
                u"GROUP BY u.id ORDER BY count DESC").fetchall()

        contributor_count = get_contributor_count()

        toolkit.c.num_contributors = [
            {u'date': datetime.now() - timedelta(days=7), u'count': 0},
            {u'date': datetime.now(), u'count': contributor_count}, ]

        return toolkit.render(u'stats/contributors.html',
                              {u'title': u'Contributor statistics'})

    def records(self):
        '''Render the records stats page.'''

        toolkit.c.datastore_stats = toolkit.get_action(u'dataset_statistics')(
                self.context, {})
        toolkit.c.num_records = [
            {u'date': datetime.now() - timedelta(days=7), u'count': 0}, {
                u'date': datetime.now(), u'count': toolkit.c.datastore_stats[u'total']
                }, ]

        return toolkit.render(u'stats/records.html', {u'title': u'Record statistics'})

    def dataset_metrics(self, id):
        '''Render a page displaying metrics for a given dataset.

        :param id: the id of the dataset

        '''

        data_dict = {u'id': id}

        # check if package exists
        try:
            toolkit.c.pkg_dict = toolkit.get_action(u'package_show')(self.context,
                                                                     data_dict)
            toolkit.c.pkg = self.context[u'package']
        except toolkit.ObjectNotFound:
            toolkit.abort(404, toolkit._(u'Dataset not found'))
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._(u'Unauthorized to read package %s') % id)

        # If this is a new dataset, and we only have recent tracking metrics
        # We want to show stats per day, rather than per month

        # Get the oldest tracking date
        oldest_date = model.Session.query(model.TrackingSummary.tracking_date, ).filter(
                model.TrackingSummary.package_id == toolkit.c.pkg_dict[u'id']).order_by(
                model.TrackingSummary.tracking_date).limit(1).scalar()

        # If oldest date is none (no stats yet) we don't want to continue
        if oldest_date:
            # Calc difference between dates
            delta = date.today() - oldest_date

            # If we have data for more than 31 days, we'll show by month;
            # otherwise segment by day
            if delta.days > 10:
                toolkit.c.date_interval = u'month'
                label_formatter = u'%b %Y'
                rrule_interval = rrule.MONTHLY
            else:
                toolkit.c.date_interval = u'day'
                label_formatter = u'%d/%m/%y'
                rrule_interval = rrule.DAILY

            date_func = func.date_trunc(toolkit.c.date_interval,
                                        model.TrackingSummary.tracking_date)

            q = model.Session.query(date_func.label(u'date'),
                                    func.sum(model.TrackingSummary.count).label(u'sum'))

            q = q.filter(
                    and_(model.TrackingSummary.package_id == toolkit.c.pkg_dict[u'id']))
            q = q.order_by(date_func)
            q = q.group_by(date_func)

            tracking_stats = {}

            # Create a dictionary of tracking stat results
            for stat in q.all():
                # Keyed by formatted date
                formatted_date = stat.date.strftime(label_formatter)
                tracking_stats[formatted_date] = int(stat.sum)

            # https://github.com/joetsoi/flot-barnumbers
            toolkit.c.pageviews = []
            toolkit.c.pageviews_options = {
                u'grid': {
                    u'borderWidth': {u'top': 0, u'right': 0, u'bottom': 1, u'left': 1},
                    u'borderColor': u'#D4D4D4'
                    }, u'xaxis': {
                    u'ticks': [], u'tickLength': 0
                    }, u'yaxis': {
                    u'tickLength': 0
                    }, u'bars': {
                    u'show': 1,
                    u'align': u'center',
                    u'zero': 1,
                    u'lineWidth': 0.7,
                    u'barWidth': 0.9,
                    u'showNumbers': 1,
                    u'numbers': {
                        u'xAlign': 1, u'yAlign': 1, u'top': -15
                        # BS: Added this. Need to patch flot.barnumbers properly
                        }
                    }
                }

            for i, dt in enumerate(rrule.rrule(rrule_interval, dtstart=oldest_date,
                                               until=date.today())):

                formatted_date = dt.strftime(label_formatter)

                # Do we have a value from the tracking stats?
                try:
                    count = tracking_stats[formatted_date]
                except KeyError:
                    # No value - count is zero
                    count = 0

                # Add data
                toolkit.c.pageviews.append([i, count])

                # Add date label to ticks
                toolkit.c.pageviews_options[u'xaxis'][u'ticks'].append(
                        [i, formatted_date])

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

        toolkit.c.resource_downloads = []
        toolkit.c.total_downloads = 0

        endpoint = os.path.join(config.get(u'ckanpackager.url'), u'statistics')

        # FIXME: This does not work!!

        for resource in toolkit.c.pkg_dict[u'resources']:

            params = {
                u'secret': config.get(u'ckanpackager.secret'),
                u'resource_id': resource[u'id']
                }

            try:
                r = requests.post(endpoint, params)
                result = r.json()
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
                # Unable to retrieve download stats for this resource
                log.critical(
                        u'ERROR %s: Unable to retrieve download stats for resource %s',
                        r.status_code, resource[u'id'])
            except ConnectionError, e:
                log.critical(e)
            else:
                try:
                    total = int(result[u'totals'][resource[u'id']][u'emails'])
                except KeyError:
                    # We do not have stats for this resource
                    pass
                else:
                    toolkit.c.resource_downloads.append({
                        u'name': resource[u'name'],
                        u'id': resource[u'id'],
                        u'total': total
                        })

                    toolkit.c.total_downloads += total

        return toolkit.render(u'stats/dataset_metrics.html')
