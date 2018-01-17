# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict

from ckan.plugins import toolkit


class DefaultView(object):
    '''A view object, used to define custom views for records and grid view'''

    resource_id = None

    format = None

    field_groups = {}
    field_facets = []

    filter_options = {}

    # Default columns to show in grid
    grid_default_columns = []

    # Specific column widths
    grid_column_widths = {}

    # Default state
    state = {
        u'gridOptions': {
            u'defaultFormatter': u'NHMFormatter',
            u'enableCellRangeSelection': False,
            u'enableTextSelectionOnCells': False,
            u'enableCellNavigation': False,
            u'enableColumnReorder': False,
            u'defaultColumnWidth': 70
            },
        u'columnsWidth': [{
            u'column': u'_id',
            u'width': 45
            }, ],
        u'columnsTitle': [{
            u'column': u'_id',
            u'title': u''
            # This is just converted into a link so lets hide the title
            }],
        u'columnsToolTip': []
        }

    @staticmethod
    def get_ordered_fields(resource_id):
        '''Get fields ordered the same as the uploaded dataset

        :param resource_id:

        '''
        data = {
            u'resource_id': resource_id,
            u'limit': 0
            }
        try:
            result = toolkit.get_action(u'datastore_search')({}, data)
        except toolkit.ObjectNotFound:
            return []
        else:
            return [f[u'id'] for f in result[u'fields']]

    def render_record(self, c):
        '''Render a record

        :param c: 

        '''

        # The record_dict does not have fields in the correct order
        # So load the fields, and create an OrderedDict with field: value
        toolkit.c.field_data = OrderedDict()

        for field in self.get_ordered_fields(toolkit.c.resource[u'id']):
            if not field.startswith(u'_'):
                toolkit.c.field_data[field] = toolkit.c.record_dict.get(field, None)

        return toolkit.render(u'record/view.html')

    def get_field_groups(self, resource):
        '''

        :param resource: 

        '''
        return self.field_groups

    def get_slickgrid_state(self):
        ''' '''
        return self.state
