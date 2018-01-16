
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from ckanext.nhm.views import *


def resource_view_get_view(resource):
    '''Retrieve the controller for a resource
    Try and match on resource ID, or on format
    So we can provide a custom controller for all format types - e.g. DwC

    :param resource: return: controller class
    :returns: controller class

    '''

    subclasses = DefaultView.__subclasses__()

    for cls in subclasses:
        # Does the resource ID match the record controller
        if cls.resource_id == resource[u'id']:
            return cls()

    # Or do we have a controller for a particular format type (eg. DwC)
    # Run in separate loop so this is lower specificity
    for cls in subclasses:
        if cls.format == resource[u'format']:
            return cls()

    return DefaultView()


def resource_view_get_filter_options(resource):
    '''Return additional filter options for a resource view

    :param resource: resource dict
    :returns: OrderedDict of filter options

    '''
    view_cls = resource_view_get_view(resource)
    return view_cls.filter_options
