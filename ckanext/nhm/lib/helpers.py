
import logging
import ckan.model as model
import ckan.logic as logic
from datetime import datetime
import ckan.lib.formatters as formatters
import urllib

# All funcs will be made available as helpers
from webhelpers.number import format_data_size

log = logging.getLogger(__name__)

def get_site_statistics():
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

    return record.get('title', None) or record.get('name', None) or 'Record %s' % record.get('_id', 'Unknown')


def keemu_record_display_name(record):

    # Get the name to display for a KE EMu record

    # Get name for specific record type
    if record.type == 'artefact' and record.name:
        return record.name
    # Trying to access a non existent property will cause a session error - check first
    elif hasattr(record, 'catalogue_number') and record.catalogue_number:
        return 'Catalogue record %s' % record.catalogue_number

    return 'Record %s' % record.irn


def keemu_render_datetime(datetime_):
    # Datetime formatter

    # Convert data to datetime
    datetime_ = datetime.combine(datetime_, datetime.min.time())
    return formatters.localised_nice_date(datetime_, show_date=True)