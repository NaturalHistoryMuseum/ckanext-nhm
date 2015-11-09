#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from pylons import config
import requests

MAM_MEDIA_ENDPOINT = 'https://web-dm-1.nhm.ac.uk:8443/activiti-rest/service/runtime/process-instances'


def mam_media_request(asset_id, email):
    """
    Request an original image from MAM
    :param asset_id: MAM asset ID
    :param email: email to send to
    :return:
    """
    data = {
        "processDefinitionKey": "original-media-request",
        "variables": [
            {"name": "emailAddress", "value": email},
            {"name": "assets", "value": asset_id}
        ]
    }
    r = requests.post(MAM_MEDIA_ENDPOINT, json=data, auth=(config.get("ckanext.nhm.mam.username"), config.get("ckanext.nhm.mam.password")), verify=False)
    # Raise an exception for an error
    r.raise_for_status()