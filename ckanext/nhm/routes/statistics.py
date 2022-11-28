# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
import json
import zlib
import base64
from collections import OrderedDict
from datetime import datetime

import ckan.model as model
from ckan.lib.search import make_connection
from ckan.plugins import toolkit
from flask import Blueprint
from sqlalchemy import func, false

from ckanext.nhm.lib.helpers import get_record_stats

# create a flask blueprint with a prefix
blueprint = Blueprint(
    name='statistics', import_name=__name__, url_prefix='/about/statistics'
)


def _context():
    return {
        'user': toolkit.c.user or toolkit.c.author,
        'auth_user_obj': toolkit.c.userobj,
    }


@blueprint.before_request
def before_request():
    """
    set context and check authorization.
    """
    try:
        toolkit.check_access('site_read', _context())
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._('Not authorized to see this page'))


@blueprint.route('/resources')
def resources():
    """
    Render the resources statistics page.
    """

    # segment by day (further grouping can be done by d3)
    toolkit.c.date_interval = 'day'

    date_func = func.date_trunc(toolkit.c.date_interval, model.Resource.created)

    q = model.Session.query(date_func.label('date'), func.count().label('count'))

    q = q.order_by(date_func).group_by(date_func)

    graph_data = []
    total = 0

    for stat in q.all():
        total += stat.count
        formatted_date = stat.date.strftime('%Y-%m-%d')
        graph_data.append([formatted_date, total])

    # compress the data
    toolkit.c.graph_data = base64.b64encode(
        zlib.compress(json.dumps(graph_data).encode(), level=9)
    )

    return toolkit.render('stats/resources.html', {'title': 'Resource statistics'})


@blueprint.route('/records')
def records():
    """
    Render the records stats page.
    """

    toolkit.c.datastore_stats = toolkit.get_action('dataset_statistics')(_context(), {})

    record_stats = get_record_stats()
    graph_data = [[x['date'].strftime('%Y-%m-%d'), x['count']] for x in record_stats]

    # compress the data
    toolkit.c.graph_data = base64.b64encode(
        zlib.compress(json.dumps(graph_data).encode(), level=9)
    )

    return toolkit.render('stats/records.html', {'title': 'Record statistics'})


@blueprint.route('/contributors')
def contributors():
    """
    Render the contributors statistics page.
    """

    graph_data = []

    # we use solr to get the number of authors for the front page statistics so we'll use it again
    # here to get a per-package authors count. We have to use solr directly to do this because the
    # package_search action doesn't allow the pivot options to be passed through
    solr = make_connection()
    results = (
        solr.search(
            '*:*',
            **{
                'fq': '+capacity:public +state:active',
                'facet': 'true',
                'facet.pivot': 'id,author',
                'facet.pivot.mincount': 1,
                'facet.limit': -1,
            }
        )
        .facets.get('facet_pivot', {})
        .get('id,author', [])
    )

    # turn the counts into a lookup from package_id -> number of authors. Note that the number of
    # authors only includes authors we haven't seen before to avoid counting authors of multiple
    # packages more than once
    counts = {}
    seen_authors = set()
    for hit in results:
        package_id = hit['value']
        package_authors = set(author['value'] for author in hit.get('pivot', []))
        # figure out which authors have not been counted yet
        unseen_authors = package_authors.difference(seen_authors)
        counts[package_id] = len(unseen_authors)
        seen_authors.update(unseen_authors)

    # retrieve the packages in the database ordered by creation time. We need this because we can't
    # order the solr facets by created date
    order = list(
        model.Session.query(model.Package.id, model.Package.metadata_created)
        .filter(model.Package.private == false())
        .filter(model.Package.state == model.State.ACTIVE)
        .order_by(model.Package.metadata_created)
    )

    # only do stuff if we have some packages
    if order:
        # always segment by day (further grouping can be done by d3)
        extraction_format = '%Y-%m-%d'

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

        total = 0
        # run through the data, adding up a total as we go and adding the data to the graph
        for i, (formatted_date, count) in enumerate(grouped_ordered_data.items()):
            total += count
            graph_data.append([formatted_date, total])

    # compress the data
    toolkit.c.graph_data = base64.b64encode(
        zlib.compress(json.dumps(graph_data).encode(), level=9)
    )

    return toolkit.render(
        'stats/contributors.html', {'title': 'Contributor statistics'}
    )
