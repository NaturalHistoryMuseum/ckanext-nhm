# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging

import requests
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


def cache_clear_nginx_proxy():
    '''Clear NGINX Proxy Cache - issue PURGE request to load balancer.'''
    url = toolkit.config.get('ckan.site_url')

    # Prepare a PURGE request to send to front end proxy
    req = requests.Request('PURGE', url)
    s = requests.Session()
    try:
        r = s.send(req.prepare(), timeout=0.5)
        r.raise_for_status()
    except:
        log.warning('Error clearing NGINX cache')
