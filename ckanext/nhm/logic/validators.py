
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import re
import ckan.plugins as p
from ckan.common import _

Invalid = p.toolkit.Invalid


def string_max_length(max_length):
    '''Checks if a string is longer than a certain length

    :param max_length: 

    '''
    def callable(value, context):
        '''

        :param value: 
        :param context: 

        '''

        if len(value) > max_length:
            raise Invalid(
                _(u'Length must be less than {0} characters')
                .format(max_length)
            )

        return value

    return callable

uuid_re = re.compile(u'^[\w]{40}$')


def uuid_validator(value, context):
    '''Checks if a UUID is valid (used for MAM asset IDs)
    We check with a regex as MAM assets ids aren't valid UUID

    :param value: param context:
    :param context: 

    '''
    if uuid_re.match(value):
        return value
    else:
        raise Invalid(_(u'Invalid Asset ID'))
