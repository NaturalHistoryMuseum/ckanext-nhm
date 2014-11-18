#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


def list_to_form_options(values, allow_empty=False, allow_empty_text='None'):
    """
    Format a list of values into a list of dict suitable for use in forms: [{value: x, name: y}]
    @param values: list or list of tuples [(value, name)]
    @param allow_empty: If true, will add none option
    @param allow_empty_name: Label for none value
    @return:
    """
    options = []

    if allow_empty:
        options.append({'value': None, 'text': allow_empty_text or None})

    for value in values:

        if isinstance(value, basestring):
            name = value
        else:
            # If this is a tuple or list use (value, name)
            name = value[1]
            value = value[0]

        options.append({'value': value, 'text': name})

    return options