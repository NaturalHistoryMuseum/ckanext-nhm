# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from datetime import datetime, timedelta
import time

from ckanext.nhm.lib.helpers import get_record_stats
from flask import Blueprint
from sqlalchemy import func

import ckan.model as model
from ckan.plugins import toolkit

# create a flask blueprint with a prefix
blueprint = Blueprint(name=u'statistics', import_name=__name__,
                      url_prefix=u'/about/statistics')


def _context():
    return {
        u'user': toolkit.c.user or toolkit.c.author,
        u'auth_user_obj': toolkit.c.userobj
        }


@blueprint.before_request
def before_request():
    u'''set context and check authorization'''
    try:
        toolkit.check_access(u'site_read', _context())
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._(u'Not authorized to see this page'))


@blueprint.route('/resources')
def resources():
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
            u'lines': {
                u'show': True
                },
            u'points': {
                u'show': True
                }
            },
        u'xaxis': {
            u'mode': u'time',
            u'ticks': []
            },
        u'yaxis': {
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
                          {
                              u'title': u'Resource statistics'
                              })


@blueprint.route('/records')
def records():
    '''Render the records stats page.'''

    toolkit.c.datastore_stats = toolkit.get_action(u'dataset_statistics')(
        _context(), {})

    toolkit.c.num_records = get_record_stats()

    return toolkit.render(u'stats/records.html', {
        u'title': u'Record statistics'
        })
