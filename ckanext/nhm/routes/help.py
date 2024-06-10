# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint

# create a flask blueprint with a prefix
blueprint = Blueprint(name='help', import_name=__name__, url_prefix='/help')


@blueprint.route('/')
@blueprint.route('')
def index():
    """
    Render the help index.
    """
    return toolkit.render('help/index.html', {'title': 'Help'})


@blueprint.route('/search')
def search():
    """
    Render the help page for integrated search.
    """
    return toolkit.render('help/search.html', {'title': 'Integrated Search Help'})


@blueprint.route('/dataset-permissions')
def permissions():
    """
    Render the help page for dataset permissions.
    """
    return toolkit.render(
        'help/permissions.html', {'title': 'Dataset Permissions Help'}
    )
