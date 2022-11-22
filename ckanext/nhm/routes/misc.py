# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint, jsonify

# create a flask blueprint with a prefix
blueprint = Blueprint(name='misc', import_name=__name__)


@blueprint.route('/tm_reduced_redundancy_<random_string>')
@blueprint.route('/server_status/')
def redundancy(random_string=None):
    """
    This is a hacky fix for data-portal#422, just so calling this page doesn't return a
    404 and fill up the logs.
    """
    return jsonify({})
