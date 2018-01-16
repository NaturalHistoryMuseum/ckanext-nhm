
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


def list_to_form_options(values, allow_empty=False, allow_empty_text=u'None'):
    '''Format a list of values into a list of dict suitable for use in forms: [{value: x, name: y}]

    :param values: list or list of tuples [(value, name)]
    :param allow_empty: If true, will add none option (Default value = False)
    :param allow_empty_name: Label for none value
    :param allow_empty_text:  (Default value = u'None')

    '''
    options = []

    if allow_empty:
        options.append({u'value': None, u'text': allow_empty_text or None})

    for value in values:

        if isinstance(value, basestring):
            name = value
        else:
            # If this is a tuple or list use (value, name)
            name = value[1]
            value = value[0]

        options.append({u'value': value, u'text': name})

    return options
