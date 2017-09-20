#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '20/08/2017'.
"""

from ckanext.nhm.views import *


def resource_view_get_view(resource):
    """
    Retrieve the controller for a resource
    Try and match on resource ID, or on format
    So we can provide a custom controller for all format types - e.g. DwC
    @param resource:
    @return: controller class
    """

    subclasses = DefaultView.__subclasses__()

    for cls in subclasses:
        # Does the resource ID match the record controller
        if cls.resource_id == resource['id']:
            return cls()

    # Or do we have a controller for a particular format type (eg. DwC)
    # Run in separate loop so this is lower specificity
    for cls in subclasses:
        if cls.format == resource['format']:
            return cls()

    return DefaultView()


def resource_view_get_filter_options(resource):
    """

    Return additional filter options for a resource view
    @param resource: resource dict
    @return: OrderedDict of filter options
    """
    view_cls = resource_view_get_view(resource)
    return view_cls.filter_options
