#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from datetime import datetime as dt
from datetime import timedelta, timezone

import requests
from cachetools import TTLCache, cached
from ckan.plugins import toolkit


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get_iiif_status():
    health = {'ping': False}

    url = toolkit.config.get('ckanext.iiif.image_server_url')
    try:
        r = requests.get(url + '/status', timeout=7)
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


@cached(cache=TTLCache(maxsize=10, ttl=600))
def get_ingest_status():
    current_version = toolkit.get_action('vds_version_round')(
        {},
        {'resource_id': toolkit.config.get('ckanext.nhm.specimen_resource_id')},
    )
    last_ingest_timestamp = dt.fromtimestamp(current_version / 1000, tz=timezone.utc)
    last_ingest_date = last_ingest_timestamp.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    right_now = dt.now(timezone.utc)
    day_of_week = right_now.weekday()
    today = right_now.replace(hour=0, minute=0, second=0, microsecond=0)
    is_before_10am = right_now.hour < 10
    is_before_12pm = right_now.hour < 12  # give it a couple of hours to process
    expected_offsets_early = [1, 1, 1, 1, 1, 2, 3]
    expected_offsets_late = [0, 0, 0, 0, 1, 2, 0]

    last_ingest_date_offset = (last_ingest_date - today).days
    current_expected_offset = (
        expected_offsets_early[day_of_week]
        if is_before_10am
        else expected_offsets_late[day_of_week]
    )
    state = 'good' if last_ingest_date_offset == current_expected_offset else 'bad'
    if (
        (not is_before_10am)
        and is_before_12pm
        and last_ingest_date_offset == expected_offsets_early[day_of_week]
    ):
        state = 'ok'

    next_ingest_offsets_early = [0, 0, 0, 0, 2, 1, 0]
    next_ingest_offsets_late = [1, 1, 1, 3, 2, 1, 1]
    next_ingest = today + timedelta(
        days=next_ingest_offsets_early[day_of_week]
        if is_before_10am and last_ingest_date_offset != 0
        else next_ingest_offsets_late[day_of_week]
    )

    return {
        'current_version': last_ingest_date.strftime('%Y-%m-%d'),
        'state': state,
        'next_ingest': next_ingest.strftime('%Y-%m-%d'),
    }
