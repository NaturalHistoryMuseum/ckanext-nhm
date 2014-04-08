
import logging
import ckan.model as model
import ckan.logic as logic
from datetime import datetime
import ckan.lib.formatters as formatters
import urllib
from collections import OrderedDict
# All funcs will be made available as helpers
from webhelpers.number import format_data_size
import os
from ckanext.nhm.lib.keemu import IDENTIFIER_PREFIX

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