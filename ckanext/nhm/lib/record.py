
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import ckan.model as model
import ckan.logic as logic
from ckan.common import c
from ckanext.nhm.dcat.utils import rdf_resources

get_action = logic.get_action

def get_record_by_uuid(uuid):
    '''

    :param uuid: 

    '''

    # Loop through all resources, and try and find the record
    # Need to loop as this works for all specimens, indexlots and artefacts

    context = {u'model': model, u'session': model.Session, u'user': c.user or c.author}
    for resource_id in rdf_resources():
        try:
            # Load the resource via model so we have access to get_package_id
            resource = model.Resource.get(resource_id)
            # Retrieve datastore record
            search_result = get_action(u'datastore_search')(context, {u'resource_id': resource_id, u'filters': {u'occurrenceID': uuid}})
            record = search_result[u'records'][0]
        except:
            pass
        else:
            return record, resource
