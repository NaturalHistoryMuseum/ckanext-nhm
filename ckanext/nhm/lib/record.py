#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from typing import Optional

import ckan.model as model
from cachetools import cached, TTLCache
from ckan.plugins import toolkit
from ckanext.nhm.dcat.utils import rdf_resources
from ckanext.nhm.lib.helpers import get_specimen_resource_id
from contextlib import suppress


def get_record_by_uuid(uuid, version=None):
    '''
    Loop through all resources, and try and find the record. Currently this only works for
    specimens (as rdf_resources() only returns the specimens resource).

    '''

    context = {'user': toolkit.c.user or toolkit.c.author}
    for resource_id in rdf_resources():
        try:
            # load the resource via model so we have access to get_package_id
            resource = model.Resource.get(resource_id)

            # then search for the record
            search_data_dict = {
                'resource_id': resource_id,
                'filters': {
                    'occurrenceID': uuid,
                },
                'version': version,
            }
            # retrieve datastore record
            search_result = toolkit.get_action('datastore_search')(context, search_data_dict)
            record = search_result['records'][0]
        except:
            pass
        else:
            return record, resource

    return None, None


# cache for 5 mins
@cached(cache=TTLCache(maxsize=4096, ttl=300))
def get_specimen_by_uuid(uuid: str, version: Optional[int] = None) -> Optional[dict]:
    with suppress(Exception):
        search_data_dict = {
            'resource_id': get_specimen_resource_id(),
            'filters': {
                'occurrenceID': uuid,
            },
            'version': version,
        }
        search_result = toolkit.get_action('datastore_search')({}, search_data_dict)
        return search_result['records'][0]

    return None
