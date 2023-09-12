#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


def list_to_form_options(values, allow_empty=False, allow_empty_text="None"):
    """
    Format a list of values into a list of dict suitable for use in forms. The values
    passed should either be a list of str values or a list of text, value pairs.

    The options returned will be a list of dicts: [{value: x, text: y}]. If the values
    parameter is a list of strs, the str value will be used for both the value and the
    text in each dict.

    :param values: list or list of tuples [(name, value)]
    :param allow_empty: if true, will add none option (optional, default: False)
    :param allow_empty_text: label for none value (optional, default: 'None')
    """
    options = []

    if allow_empty:
        options.append({"value": "", "text": allow_empty_text or None})

    for value in values:
        if isinstance(value, str):
            option_text = option_value = value
        else:
            # if this is a tuple or list use (name, value)
            option_text, option_value = value

        options.append({"value": option_value, "text": option_text})

    return options
