#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit
import requests


def get_iiif_status():
    health = {}

    url = toolkit.config.get('ckanext.iiif.image_server_url')
    r = requests.get(url + '/status')
    if r.ok:
        health['ping'] = True
        response_json = r.json()
    else:
        response_json = {}

    health['status'] = response_json.get('status')
    mss = response_json.get('profiles', {}).get('mss', {})
    health['specimens'] = mss.get('mss_status', {}).get('status', ':(')
    health['es'] = mss.get('es', {'status': 'red', 'response_time': None})

    return health
