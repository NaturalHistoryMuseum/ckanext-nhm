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

uuid_re = re.compile('^[\w]{40}$')


def uuid_validator(value, context):
    """
    Checks if a UUID is valid (used for MAM asset IDs)
    We check with a regex as MAM assets ids aren't valid UUID

    :raises: ckan.lib.navl.dictization_functions.Invalid if the string is
        an invalid UUID

    :param value:
    :param context:
    :return:
    """
    if uuid_re.match(value):
        return value
    else:
        raise Invalid(_('Invalid Asset ID'))
