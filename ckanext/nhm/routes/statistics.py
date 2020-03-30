# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from collections import OrderedDict
from datetime import datetime

import ckan.model as model
from ckan.lib.search import make_connection
from ckan.plugins import toolkit
from ckanext.nhm.lib.helpers import get_record_stats
from flask import Blueprint
from sqlalchemy import func

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


@blueprint.route(u'/contributors')
def contributors():
    '''
    Render the contributors statistics page.
    '''
    # we use solr to get the number of authors for the front page statistics so we'll use it again
    # here to get a per-package authors count. We have to use solr directly to do this because the
    # package_search action doesn't allow the pivot options to be passed through
    solr = make_connection()
    results = solr.search(u'*:*', **{
        u'facet': u'true',
        u'facet.pivot': u'id,author',
        u'facet.pivot.mincount': 1,
        u'facet.limit': -1,
    }).facets.get(u'facet_pivot', {}).get(u'id,author', [])

    # turn the counts into a lookup from package_id -> number of authors
    counts = {hit[u'value']: len(hit[u'pivot']) for hit in results}
    # retrieve the packages in the database ordered by creation time. We need this because we can't
    # order the solr facets by created date
    order = list(model.Session.query(model.Package.id, model.Package.metadata_created)
                 .order_by(model.Package.metadata_created))

    # get the earliest package creation date
    delta = datetime.now() - order[0][1]
    # if we have data for more than 10 days, we'll show by month; otherwise segment by day
    extraction_format = u'%b %Y' if delta.days > 10 else u'%d/%m/%y'

    # sum the counts by package creation time based on the extraction format we chose
    grouped_ordered_data = OrderedDict()
    for package_id, created in order:
        # just in case the database isn't up to date with the solr index
        if package_id not in counts:
            continue
        date_group = created.strftime(extraction_format)
        if date_group not in grouped_ordered_data:
            grouped_ordered_data[date_group] = 0
        grouped_ordered_data[date_group] += counts[package_id]

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

    # run through the data, adding up a total as we go and adding the data to the graph
    for i, (formatted_date, count) in enumerate(grouped_ordered_data.items()):
        total += count
        toolkit.c.graph_data.append([i, total])
        toolkit.c.graph_options[u'xaxis'][u'ticks'].append([i, formatted_date])

    return toolkit.render(u'stats/resources.html', {
        u'title': u'Contributor statistics'
    })
