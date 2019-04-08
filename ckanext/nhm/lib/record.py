#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import ckan.logic as logic
import ckan.model as model
from ckan.common import c
from ckanext.nhm.dcat.utils import rdf_resources

get_action = logic.get_action


def get_record_by_uuid(uuid, version=None):
    '''
    Loop through all resources, and try and find the record. Currently this only works for
    specimens (as rdf_resources() only returns the specimens resource).

    :param uuid: the uuid of the record we're looking for
    :param version: the version to find
    :return: the record dict and the resource model object
    '''
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': c.user or c.author
    }
    for resource_id in rdf_resources():
        try:
            # load the resource via model so we have access to get_package_id
            resource = model.Resource.get(resource_id)

            # then search for the record
            search_data_dict = {
                u'resource_id': resource_id,
                u'filters': {
                    u'occurrenceID': uuid,
                },
                u'version': version,
            }
            # retrieve datastore record
            search_result = get_action(u'datastore_search')(context, search_data_dict)
            record = search_result[u'records'][0]
        except:
            pass
        else:
            return record, resource
