# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict

from ckan.plugins import toolkit


class DefaultView(object):
    """
    A view object, used to define custom views for records and grid view.
    """

    resource_id = None

    format = None

    field_groups = {}
    field_facets = []

    filter_options = []

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
            'defaultColumnWidth': 70,
        },
        'columnsWidth': [
            {'column': '_id', 'width': 45},
        ],
        'columnsTitle': [
            {
                'column': '_id',
                'title': ''
                # This is just converted into a link so lets hide the title
            }
        ],
        'columnsToolTip': [],
    }

    @staticmethod
    def get_ordered_fields(resource_id):
        """
        Get fields ordered the same as the uploaded dataset.

        :param resource_id:
        """
        data = {'resource_id': resource_id, 'limit': 0}
        try:
            result = toolkit.get_action('datastore_search')({}, data)
        except toolkit.ObjectNotFound:
            return []
        else:
            return [f['id'] for f in result['fields']]

    def render_record(self, c):
        """
        Render a record.

        :param c:
        """

        # The record_dict does not have fields in the correct order
        # So load the fields, and create an OrderedDict with field: value
        toolkit.c.field_data = OrderedDict()

        for field in self.get_ordered_fields(toolkit.c.resource['id']):
            if not field.startswith('_'):
                toolkit.c.field_data[field] = toolkit.c.record_dict.get(field, None)

        return toolkit.render('record/view.html')

    def get_field_groups(self, resource):
        """
        Return the field groups.
        """
        return self.field_groups

    def get_slickgrid_state(self):
        """
        Return the state of the slickgrid.
        """
        return self.state
