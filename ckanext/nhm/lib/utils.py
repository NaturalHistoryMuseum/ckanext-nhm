#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import requests
from cachetools import TTLCache, cached
from ckan.plugins import toolkit


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get_iiif_status():
    health = {'ping': False}

    url = toolkit.config.get('ckanext.iiif.image_server_url')
    try:
        r = requests.get(url + '/status', timeout=5)
        if r.ok:
            health['ping'] = True
            response_json = r.json()
        else:
            response_json = {}
    except requests.exceptions.RequestException as e:
        response_json = {}

    health['status'] = response_json.get('status')
    mss = response_json.get('profiles', {}).get('mss', {})
    health['specimens'] = (
        mss.get('source_cache', {}).get('mss_status', {}).get('status', ':(')
    )
    health['es'] = mss.get('es', {'status': 'red', 'response_time': None})

    return health
