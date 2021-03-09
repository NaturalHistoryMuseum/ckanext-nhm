#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json
import logging

import requests
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def mam_media_request(asset_id, email):
    '''Request an original image from MAM

    :param asset_id: MAM asset ID
    :param email: email to send to

    '''
    payload = {
        'processDefinitionKey': 'original-media-request',
        'variables': [{'name': 'emailAddress', 'value': email},
                       {'name': 'assets', 'value': asset_id}]
    }
    headers = {'content-type': 'application/json'}
    auth = (toolkit.config.get('ckanext.nhm.mam.username'),
            toolkit.config.get('ckanext.nhm.mam.password'))
    r = requests.post(toolkit.config.get('ckanext.nhm.mam.endpoint'),
                      data=json.dumps(payload), auth=auth, verify=False, headers=headers)
    # Raise an exception and log the error
    try:
        r.raise_for_status()
    except:
        log.critical('Error requesting MAM image: {0}'.format(r.text))
        raise
