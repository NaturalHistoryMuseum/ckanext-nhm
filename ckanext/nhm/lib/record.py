#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import ckan.model as model
import ckan.logic as logic
from ckan.common import c
from ckanext.nhm.dcat.utils import rdf_resources

get_action = logic.get_action

def get_record_by_uuid(uuid):

    # Loop through all resources, and try and find the record
    # Need to loop as this works for all specimens, indexlots and artefacts

    context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
    for resource_id in rdf_resources():
        try:
            # Load the resource via model so we have access to get_package_id
            resource = model.Resource.get(resource_id)
            # Retrieve datastore record
            search_result = get_action('datastore_search')(context, {'resource_id': resource_id, 'filters': {'occurrenceID': uuid}})
            record = search_result['records'][0]
        except:
            pass
        else:
            return record, resource