
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.dcat.utils import catalog_uri
from ckanext.nhm.lib.helpers import get_specimen_resource_id

def object_uri(record_dict):
    '''Returns an URI for an object
    
    This will be used to uniquely reference the dataset on the RDF
    serializations.
    
    Returns a string with the dataset URI.

    :param record_dict: 

    '''

    uuid = record_dict.get(u'uuid')
    uri = u'{0}/object/{1}'.format(catalog_uri().rstrip('/'), uuid)
    return uri


def rdf_resources():
    '''


    :returns: :return:

    '''
    # FIXME - Need to add in indexlots and artefacts
    return [get_specimen_resource_id()]
