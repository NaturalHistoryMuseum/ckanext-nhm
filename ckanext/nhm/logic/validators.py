# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import re

from ckan.plugins import toolkit


def string_max_length(max_length):
    """
    Checks if a string is longer than a certain length.

    :param max_length:
    """

    def callable(value, context):
        """
        The validation function that checks if a string is longer than the max length.

        :param value: the input string
        :param context: the context
        """

        if len(value) > max_length:
            raise toolkit.Invalid(
                toolkit._(f'Length must be less than {max_length} characters')
            )

        return value

    return callable


uuid_re = re.compile(r'^[\w]{40}$')


def uuid_validator(value, context):
    """
    Checks if a UUID is valid (used for MAM asset IDs). We check with a regex as MAM
    assets ids aren't valid UUIDs.

    :param value:
    :param context:
    """
    if uuid_re.match(value):
        return value
    else:
        raise toolkit.Invalid(toolkit._('Invalid Asset ID'))
