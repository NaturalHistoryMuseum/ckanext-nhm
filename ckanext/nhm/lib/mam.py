#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import json
import requests
import logging
from pylons import config


log = logging.getLogger(__name__)


def mam_media_request(asset_id, email):
    """
    Request an original image from MAM
    :param asset_id: MAM asset ID
    :param email: email to send to
    :return:
    """
    payload = {
        "processDefinitionKey": "original-media-request",
        "variables": [
            {"name": "emailAddress", "value": email},
            {"name": "assets", "value": asset_id}
        ]
    }
    headers = {'content-type': 'application/json'}
    auth = (config.get("ckanext.nhm.mam.username"), config.get("ckanext.nhm.mam.password"))
    r = requests.post(config.get("ckanext.nhm.mam.endpoint"), data=json.dumps(payload), auth=auth, verify=False, headers=headers)
    # Raise an exception and log the error
    try:
        r.raise_for_status()
    except:
        log.critical('Error requesting MAM image: {0}'.format(r.text))
        raise
