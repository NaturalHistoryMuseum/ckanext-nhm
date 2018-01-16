
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json
import requests
import logging
from pylons import config


log = logging.getLogger(__name__)


def mam_media_request(asset_id, email):
    '''Request an original image from MAM

    :param asset_id: MAM asset ID
    :param email: email to send to

    '''
    payload = {
        u'processDefinitionKey': u'original-media-request',
        u'variables': [
            {u'name': u'emailAddress', u'value': email},
            {u'name': u'assets', u'value': asset_id}
        ]
    }
    headers = {u'content-type': u'application/json'}
    auth = (config.get(u'ckanext.nhm.mam.username'), config.get(u'ckanext.nhm.mam.password'))
    r = requests.post(config.get(u'ckanext.nhm.mam.endpoint'), data=json.dumps(payload), auth=auth, verify=False, headers=headers)
    # Raise an exception and log the error
    try:
        r.raise_for_status()
except:
        log.critical(u'Error requesting MAM image: {0}'.format(r.text))
        raise
