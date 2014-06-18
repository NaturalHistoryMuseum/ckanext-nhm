#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
import ckan.plugins as p
from ckan.common import _

Invalid = p.toolkit.Invalid

def string_max_length(max_length):
    '''
    Checks if a string is longer than a certain length

    :raises: ckan.lib.navl.dictization_functions.Invalid if the string is
        longer than max length
    '''
    def callable(value, context):

        if len(value) > max_length:
            raise Invalid(
                _('Length must be less than {0} characters')
                .format(max_length)
            )

        return value

    return callable


def is_latitude(value):

    # Matches: -90 -> +90
    # And value is between -90 and 90
    if not re.match("([-+]?\d{1,2}[.]?\d+)", value) or not (-90 <= float(value) <= 90):
        raise Invalid(
            _('Invalid latitude')
        )


def is_longitude(value):

    # Matches: -180 -> +180
    # And value is between -180 and 180
    if not re.match("[-+]?(\d{1,3}[.]?\d+)", value) or not (-180 <= float(value) <= 180):
        raise Invalid(
            _('Invalid longitude')
        )
