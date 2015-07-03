#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from ckanext.nhm.lib.resource import resource_get_ordered_fields
import ckan.plugins as p
from collections import OrderedDict


class DefaultView(object):
    """
    A view object, used to define custom views for records and grid view
    """

    resource_id = None

    format = None

    field_groups = {}

    # Default columns to show in grid
    grid_default_columns = []

    # Specific column widths
    grid_column_widths = {}

    # Default state
    state = {
        'gridOptions': {
            'defaultFormatter': 'NHMFormatter',
            'enableCellRangeSelection': False,
            'enableTextSelectionOnCells': False,
            'enableCellNavigation': False,
            'enableColumnReorder': False,
            'defaultColumnWidth': 50
        },
        'columnsWidth': [
            {
                'column': '_id',
                'width': 45
            },
        ],
        'columnsTitle': [
            {
                'column': '_id',
                'title': ''  # This is just converted into a link so lets hide the title
            }
        ],
        'columnsToolTip': []
    }

    def render_record(self, c):
        """
        Render a record
        """

        # The record_dict does not have fields in the correct order
        # So load the fields, and create an OrderedDict with field: value
        c.field_data = OrderedDict()
        for field in resource_get_ordered_fields(c.resource['id']):
            if not field.startswith('_'):
                c.field_data[field] = c.record_dict.get(field, None)

        return p.toolkit.render('record/view.html')

    def get_field_groups(self, resource):
        return self.field_groups

    def get_slickgrid_state(self):
        return self.state