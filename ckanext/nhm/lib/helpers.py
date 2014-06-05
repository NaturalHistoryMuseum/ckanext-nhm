
import logging
import ckan.model as model
import ckan.logic as logic
from datetime import datetime
import ckan.lib.formatters as formatters
import urllib
from collections import OrderedDict
# All funcs will be made available as helpers
from webhelpers.number import format_data_size
from ckanext.nhm.lib.dwc import DwC
import os
import json

log = logging.getLogger(__name__)

def get_site_statistics():
    # TODO: TEMP: Just to put some stats on the home page
    stats = {}
    stats['dataset_count'] = logic.get_action('package_search')(
        {}, {"rows": 1})['count']
    result = model.Session.execute(
        '''select count(*) from related r
           left join related_dataset rd on r.id = rd.related_id
           where rd.status = 'active' or rd.id is null''').first()[0]
    stats['related_count'] = result

    return stats


def record_display_name(record):
    # Get the name to display for a record
    # TODO: Need to have a form for adding what field to use
    return record.get('title', None) or record.get('name', None) or record.get('name', None) or 'Record %s' % record.get('_id', 'Unknown')


def fields_have_content(record, fields):
    """
    See if any one of a list fo fields have content
    @param record:
    @param fields: fields to check exist
    @return: True
    """
    for field in fields:

        # Ensure it's a list
        if not isinstance(field, list):
            field = [field]

        for f in field:
            if record.get(f, None):
                return True


def keemu_render_datetime(datetime_):
    # Datetime formatter

    # Convert data to datetime
    datetime_ = datetime.combine(datetime_, datetime.min.time())
    return formatters.localised_nice_date(datetime_, show_date=True)


def resource_view_state(resource_view_json):
    """
    Alter the recline view resource, adding in state info
    @param resource_view_json:
    @return:
    """

    resource_view = json.loads(resource_view_json)
    resource_view['state'] = {
        'fitColumns': True,
        'enableCellRangeSelection': False,
        'enableTextSelectionOnCells': False,
        'gridOptions': {
            'defaultFormatter': 'NHMFormatter',
            'enableCellRangeSelection': False,
            'enableTextSelectionOnCells': False,
            'enableCellNavigation': False,
            'selectedCellCssClass': 'bugger'
        }
    }

    return json.dumps(resource_view)

