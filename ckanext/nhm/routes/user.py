# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
from flask import Blueprint

blueprint = Blueprint(name='nhm_user', import_name=__name__, url_prefix='/user')


@blueprint.route('/user/<username>/organisations', methods=['GET'])
def orgs(username):
    """
    Render a list of organisations that this user is a member of.

    :param username: The username
    :return: str
    """
    try:
        toolkit.check_access('user_show', {}, {'id': username})
    except toolkit.NotAuthorized:
        toolkit.abort(403, toolkit._('Not authorized to see this page'))
    user = toolkit.get_action('user_show')(
        {'for_view': True}, {'id': username, 'include_num_followers': True}
    )
    orgs_available = toolkit.get_action('organization_list_for_user')(
        {}, {'id': username, 'permission': 'read', 'include_dataset_count': True}
    )
    return toolkit.render(
        'user/organisations.html',
        extra_vars=dict(user_dict=user, organizations=orgs_available),
    )
