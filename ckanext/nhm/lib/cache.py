#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '13/11/2017'.
"""

import logging
import requests
from pylons import config

log = logging.getLogger(__name__)


def cache_clear_nginx_proxy():
    """
    Clear NGINX Procy Cache - issue PURGE request to load balancer
    @return:
    @rtype:
    """
    url = config.get("ckan.site_url")

    # Prepare a PURGE request to send to front end proxy
    req = requests.Request('PURGE', url)
    s = requests.Session()
    try:
        r = s.send(req.prepare())
        r.raise_for_status()
    except:
        log.critical('Error clearing NGINX Cache')
