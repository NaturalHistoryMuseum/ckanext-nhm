#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from elasticsearch_dsl import Q
from splitgill.indexing.fields import DocumentField
from splitgill.search import exists_query, term_query


class FilterOption:
    """
    Class representing a filter option.

    These are more prescribed options available on certain resources, such as the
    specimens and index lot resources, and typically are shown as tick boxes.
    """

    def __init__(self, name, label, filter_dsl, hide=False):
        """
        :param name: the name of the option, this is the name passed through in the filter
        :param label: the text to show on the frontend to the user
        :param filter_dsl: an elasticsearch-dsl query object which actually does the filter. This is
                           applied in the ckanext-nhm plugin.
        :param hide: whether to hide the filter on the frontend or show it, default is False (i.e.
                     show the filter option)
        """
        self.name = name
        self.label = label
        self.filter_dsl = filter_dsl
        self.hide = hide

    def as_dict(self):
        """
        Produces a dict with the details required by the frontend to show the filter
        options to the user.

        :returns: a dict with the name and the label for the filter
        """
        return {
            'name': self.name,
            'label': self.label,
        }


# define some simple, common filters
has_image = FilterOption('_has_image', 'Has image', exists_query('associatedMedia'))

has_lat_long = FilterOption(
    '_has_lat_long', 'Has lat/long', Q('exists', field=DocumentField.ALL_POINTS)
)

exclude_mineralogy = FilterOption(
    '_exclude_mineralogy',
    'Exclude Mineralogy',
    # note the ~ which inverts the query
    ~term_query('collectionCode', 'min'),
    hide=True,
)
