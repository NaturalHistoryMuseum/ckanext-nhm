# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint

# bbcm = big butterfly count map :)
# create a flask blueprint
blueprint = Blueprint(name='big-butterfly-count-map', import_name=__name__)


@blueprint.route('/big-butterfly-count-map')
def bbcm():
    """
    Render the big butterfly count map page.
    """
    return toolkit.render('bbcm.html', {})
