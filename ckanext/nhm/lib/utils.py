#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from datetime import datetime as dt
from datetime import time, timedelta, timezone

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
    # set last ingest timestamp
    last_ingest_date = dt.fromtimestamp(current_version / 1000, tz=timezone.utc)
    # set parameters for check
    right_now = dt.now(timezone.utc)
    ingest_days = {6, 0, 1, 2, 3}
    ingest_time = time(10, 0)
    grace_time = timedelta(hours=2)

    # finds the last scheduled ingest
    temp_day = right_now
    # if its before 10 start from day before
    if right_now.hour < 10:
        temp_day -= timedelta(days=1)
    # loop back until find last time it was scheduled to ingest
    while True:
        if temp_day.weekday() in ingest_days:
            scheduled = dt.combine(temp_day.date(), ingest_time, tzinfo=timezone.utc)
            if scheduled <= right_now:
                last_scheduled = scheduled
                break
        temp_day -= timedelta(days=1)

    # find the penultimate scheduled ingest to check if ingest should allow for grace period
    temp_day = right_now - timedelta(days=1)
    # if its before 10 start from day before
    if right_now.hour < 10:
        temp_day -= timedelta(days=1)
    while True:
        if temp_day.weekday() in ingest_days:
            scheduled = dt.combine(temp_day.date(), ingest_time, tzinfo=timezone.utc)
            if scheduled <= right_now:
                penultimate_scheduled = scheduled
                break
        temp_day -= timedelta(days=1)

    # find the next scheduled ingest
    temp_day = right_now
    while True:
        if temp_day.weekday() in ingest_days:
            scheduled = dt.combine(temp_day.date(), ingest_time, tzinfo=timezone.utc)
            if scheduled > right_now:
                next_ingest = scheduled
                break
        temp_day += timedelta(days=1)

    # check if last ingest is after last scheduled ingest and is on the day expected
    if (
        last_ingest_date >= last_scheduled
        and last_ingest_date.date() == last_scheduled.date()
    ):
        state = 'good'
    else:
        # check if it should allow for grace period
        if (
            right_now <= last_scheduled + grace_time
            and last_ingest_date >= penultimate_scheduled
        ):
            state = 'ok'
        else:
            state = 'bad'

    return {
        'current_version': last_ingest_date.strftime('%Y-%m-%d'),
        'state': state,
        'next_ingest': next_ingest.strftime('%Y-%m-%d'),
    }


@cached(cache=TTLCache(maxsize=10, ttl=7200))
def get_gbif_status():
    gbif_dataset_key = toolkit.config.get('ckanext.gbif.dataset_key')
    gbif_url = (
        f'https://api.gbif.org/v1/dataset/{gbif_dataset_key}'
        if gbif_dataset_key
        else None
    )

    status_text = 'unknown'
    status_type = 'bad'

    if gbif_url:
        try:
            headers = {'User-Agent': 'NHMUK dataset status: data [at] nhm.ac.uk'}
            r = requests.get(gbif_url, timeout=7, headers=headers)
            if r.ok:
                response_json = r.json()
                modified = response_json.get('modified')
            else:
                modified = None
        except Exception as e:
            modified = None

        if modified:
            modified_datetime = dt.strptime(str(modified), '%Y-%m-%dT%H:%M:%S.%f%z')
            now = dt.now(timezone.utc)
            time_diff = now - modified_datetime
            # Check if modified date is within last 7 days
            if time_diff < timedelta(days=7):
                status_type = 'good'
            # Display last modified date
            status_text = modified_datetime.strftime('%Y-%m-%d')

    return status_text, status_type
