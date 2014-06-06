
import logging
import json
import ckan.model as model
import ckan.logic as logic
from datetime import datetime
import ckan.lib.formatters as formatters
import urllib
from collections import OrderedDict
# All funcs will be made available as helpers
from webhelpers.number import format_data_size
import os
<<<<<<< HEAD
from ckanext.nhm.lib.keemu import IDENTIFIER_PREFIX
=======
import json
>>>>>>> ckan-1251-1725-custom

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

        if isinstance(field, tuple):
            field = field[0]

        if record.get(field, None):
            return True


def unique_identifier(id):
    return '%s%s' % (IDENTIFIER_PREFIX, id)

def get_record_point(rec):

    # TODO: What should happen if lat/lon not sane?
    if rec['decimalLatitude'] and rec['decimalLongitude']:

        return json.dumps({
            'type': 'Point',
            'coordinates': [rec['decimalLongitude'], rec['decimalLatitude']]
        })

    return None

def parse_dynamic_properties(rec):

    properties = {}

    for prop in rec['dynamicProperties'].strip().split(';'):
        try:
            key, value = prop.strip().split('=')
        except ValueError:
            pass
        else:

            properties[key] = value

    return properties

<<<<<<< HEAD
=======

def keemu_render_datetime(datetime_):
    # Datetime formatter
>>>>>>> ckan-1251-1725-custom


<<<<<<< HEAD
    # {% for properties in rec.dynamicProperties.split(';'): %}
    #     {% if properties: %}
    #
    #         {% set values = properties.split('=') %}
    #         {{ values }}
    #
    #     {% endif %}
    # {% endfor %}
    #  {% do rec.update([tuple(property.strip().split('='))]) %}
=======

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

>>>>>>> ckan-1251-1725-custom
