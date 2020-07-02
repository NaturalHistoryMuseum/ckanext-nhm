#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.nhm.dcat.utils import rdf_resources

import ckan.model as model
from ckan.plugins import toolkit


def get_record_by_uuid(uuid, version=None):
    '''
    Loop through all resources, and try and find the record. Currently this only works for
    specimens (as rdf_resources() only returns the specimens resource).

    '''

    context = {u'user': toolkit.c.user or toolkit.c.author}
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
            search_result = toolkit.get_action(u'datastore_search')(context, search_data_dict)
            record = search_result[u'records'][0]
        except:
            pass
        else:
            return record, resource

    return None, None
