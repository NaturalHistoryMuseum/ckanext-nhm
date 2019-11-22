#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from elasticsearch_dsl import Q


class FilterOption(object):
    '''
    Class representing a filter option. These are more prescribed options available on certain
    resources, such as the specimens and index lot resources, and typically are shown as tick boxes.
    '''

    def __init__(self, name, label, filter_dsl, hide=False):
        '''
        :param name: the name of the option, this is the name passed through in the filter
        :param label: the text to show on the frontend to the user
        :param filter_dsl: an elasticsearch-dsl query object which actually does the filter. This is
                           applied in the ckanext-nhm plugin.
        :param hide: whether to hide the filter on the frontend or show it, default is False (i.e.
                     show the filter option)
        '''
        self.name = name
        self.label = label
        self.filter_dsl = filter_dsl
        self.hide = hide

    def as_dict(self):
        '''
        Produces a dict with the details required by the frontend to show the filter options to the
        user.

        :return: a dict with the name and the label for the filter
        '''
        return {
            u'name': self.name,
            u'label': self.label,
        }


# define some simple, common filters
has_image = FilterOption(u'_has_image', u'Has image', Q(u'exists', field=u'data.associatedMedia'))

has_lat_long = FilterOption(u'_has_lat_long', u'Has lat/long', Q(u'exists', field=u'meta.geo'))

exclude_mineralogy = FilterOption(u'_exclude_mineralogy', u'Exclude Mineralogy',
                                  # note the ~ which inverts the query
                                  ~Q(u'term', **{u'data.collectionCode': u'min'}),
                                  hide=True)
