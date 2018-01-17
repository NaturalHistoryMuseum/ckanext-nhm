#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.nhm.dcat.utils import rdf_resources

import ckan.model as model
from ckan.plugins import toolkit


def get_record_by_uuid(uuid):
    '''Get record details from its UUID. Loop through all resources, and try and find
    the record. Need to loop as this works for all specimens, indexlots and artefacts.

    :param uuid: the record's UUID.

    '''

    context = {u'user': toolkit.c.user or toolkit.c.author}
    for resource_id in rdf_resources():
        try:
            # Load the resource via model so we have access to get_package_id
            # (TODO: check for 2.8.0a)
            resource = model.Resource.get(resource_id)
            # Retrieve datastore record
            search_result = toolkit.get_action(u'datastore_search')(context, {
                u'resource_id': resource_id, u'filters': {u'occurrenceID': uuid}
                })
            record = search_result[u'records'][0]
        except:
            pass
        else:
            return record, resource
