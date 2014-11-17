#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from ckan.common import request

# Filter used for filter groups
FIELD_GROUP_FILTER = '_field_group'


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


def parse_request_filters():
    """
    Get the filters from the request object
    @return:
    """
    filter_dict = {}

    try:
        filter_params = request.params.get('filters').split('|')
    except AttributeError:
        return {}

    filter_params = filter(None, filter_params)

    for filter_param in filter_params:
        field, value = filter_param.split(':', 1)

        try:
            filter_dict[field].append(value)
        except KeyError:
            filter_dict[field] = [value]

    return filter_dict


def get_resource_filters(resource):
    """
    Parse request and return dictionary of resource filters
    This is used in the helper functions get_resource_filter_pills() and get_resource_field_groups()
    @param resource:
    @return:
    """

    filter_dict = parse_request_filters()

    def get_pill_filters(exclude_field, exclude_value):
        """
        Build filter, using filters which aren't exclude_field=exclude_value
        @param exclude_field:
        @param exclude_value:
        @return:
        """

        filters = []
        for field, values in filter_dict.items():
            for value in values:
                if not (field == exclude_field and value == exclude_value):
                    filters.append('%s:%s' % (field, value))

        return '|'.join(filters)

    pills = {}

    options = resource_filter_options(resource)
    for field, values in filter_dict.items():
        for value in values:
            filters = get_pill_filters(field, value)

            #  If this is the _tmgeom field, we don't want to output the whole value as it's in the format:
            # POLYGON ((-100.45898437499999 41.902277040963696, -100.45898437499999 47.54687159892238, -92.6806640625 47.54687159892238, -92.6806640625 41.902277040963696, -100.45898437499999 41.902277040963696))
            if field == '_tmgeom':
                pills['geometry'] = {'Polygon': filters}
            elif field in options:
                label = options[field]['label']
                try:
                    pills['options'][label] = filters
                except KeyError:
                    pills['options'] = {label: filters}
            else:
                try:
                    pills[field][value] = filters
                except KeyError:
                    pills[field] = {value: filters}

    return pills