#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

def resource_filter_options(resource):
    """
    Return the list of filter options for the given resource.

    Note that this is the master source for the list of available options.

    We may want to have this dependent on available fields (rather than
    resource format), so it's useful to keep this as a function (rather
    than a static dict).

    @type resource: dict
    @param resource: Dictionary representing a resource
    @rtype: dict
    @return: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - sql: Optional. The SQL WHERE statement to use when this
                       option is checked (as a tuple containing statement
                       and value replacements);
                - sql_false: Optional. The SQL WHERE statement to use when
                             this option is unchecked (as a tuple containing
                             statement and value replacements).
    """
    table = resource['id']
    # Get the resource-dependent filter option list
    if resource['format'].lower() == 'dwc':
        return {
            '_has_type': {
                'label': 'Has type',
                'sql': ('"{}"."typeStatus" IS NOT NULL'.format(table),)
            },
            '_has_image': {
                'label': 'Has image',
                'sql': ('"{}"."associatedMedia" IS NOT NULL'.format(table),)
            },
            '_has_lat_long': {
                'label': 'Has lat/long',
                'sql': ('"{}"."_geom" IS NOT NULL'.format(table),)
            },
            '_exclude_centroid': {
                'label': 'Exclude centroids',
                'sql': ('NOT (LOWER("{}"."Centroid") = ANY(\'{{true,yes,1}}\'))'.format(table),)
            }
        }
    else:
        return {}