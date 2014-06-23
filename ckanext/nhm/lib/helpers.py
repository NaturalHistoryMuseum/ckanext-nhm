
import logging
import json
import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import itertools
from ckanext.issues.model import Issue, ISSUE_STATUS
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from pylons import config
from ckan.common import c, _
from ckan.lib.helpers import url_for, link_to
from collections import OrderedDict

from ckanext.nhm.logic.schema import DATASET_CATEGORY, UPDATE_FREQUENCIES

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action


def get_site_statistics():
    stats = dict()
    stats['dataset_count'] = logic.get_action('package_search')({}, {"rows": 1})['count']
    # Get a count of all distinct user IDs
    stats['contributor_count'] = model.Session.execute("SELECT COUNT(DISTINCT creator_user_id) from package").scalar()

    # TODO: Get all records count
    stats['record_count'] = 3500000
    return stats


def _get_action(action, params):
    """
    Call basic get_action from template
    @param action:
    @param params:
    @return:
    """

    context = {'ignore_auth': True, 'for_view': True}

    try:
        return get_action(action)(context, params)
    except (NotFound, NotAuthorized):
        pass

    return None


def get_resource(resource_id):
    return _get_action('resource_show', {'id': resource_id})


def get_record(resource_id, record_id):
    return _get_action('record_get', {'resource_id': resource_id, 'record_id': record_id})


def record_display_name(resource, record):
    title_field = resource.get('_title_field', None)
    display_name = record.get(title_field, 'Record %s' % record.get('_id'))
    return str(display_name)


def resource_view_state(resource_view_json):
    """
    Alter the recline view resource, adding in state info
    @param resource_view_json:
    @return:
    """
    resource_view = json.loads(resource_view_json)
    resource_view['state'] = {
        'fitColumns': True,
        'gridOptions': {
            'defaultFormatter': 'NHMFormatter',
            'enableCellRangeSelection': False,
            'enableTextSelectionOnCells': False,
            'enableCellNavigation': False,
        }
    }

    return json.dumps(resource_view)


def get_datastore_fields(resource_id):
    """
    Get list of fields for a resource
    @param resource_id:
    @return: list
    """

    data = {'resource_id': resource_id, 'limit': 0}
    try:
        return toolkit.get_action('datastore_search')({}, data)['fields']
    except NotFound:
        pass

    return []


def form_select_datastore_field_options(resource_id=None, allow_empty=False):

    # Need to check for resource_id as this form gets loaded on add, nut just edit
    # And on add there will be no resource_id
    if resource_id:
        datastore_fields = [f['id'] for f in get_datastore_fields(resource_id)]
        return list_to_form_options(datastore_fields)

    return []


def form_select_update_frequency_options():
    return list_to_form_options(UPDATE_FREQUENCIES)


def list_to_form_options(values, allow_empty=False, allow_empty_text='- None -'):
    """
    Format a list of values into a list of dict suitable for use in forms: [{value: x, name: y}]
    @param values: list or list of tuples [(value, name)]
    @param allow_empty: If true, will add none option
    @param allow_empty_name: Label for none value
    @return:
    """
    options = []

    if allow_empty:
        options.append({'value': None, 'text': allow_empty_text or None})

    for value in values:

        if isinstance(value, basestring):
            name = value
        else:
            # If this is a tuple or list use (value, name)
            name = value[1]
            value = value[0]

        options.append({'value': value, 'text': name})

    return options


def resource_issue_count(package_id):

    issues_count = {}
    # Get the counts from the issues model
    result = dict(model.Session.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).filter(Issue.dataset_id==package_id).all())

    # Lop through the issue status (open and closed) and assign the count if there's a value; otherwise use 0
    for status in ISSUE_STATUS:
        try:
            issues_count[status] = result[status]
        except KeyError:
            issues_count[status] = 0

    return issues_count


def dataset_categories():
    """
    Return list of dataset category terms
    @return: list
    """
    try:
        categories = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': DATASET_CATEGORY})
        return categories
    except toolkit.ObjectNotFound:
        return None


def url_for_collection_view(view_type='recline_grid', **kwargs):
    """
    Return URL to link through to specimen dataset view, with optional search params
    @param view_type: grid to link to - grid or map
    @param kwargs: search filter params
    @return: url
    """

    resource_id = config.get("ckanext.nhm.collection_resource_id")
    context = {'model': model, 'session': model.Session, 'user': c.user}

    views = toolkit.get_action('resource_view_list')(context, {'id': resource_id})

    for view in views:
        if view['view_type'] == view_type:
            break

    return url_for(controller='package', action='resource_read', id=view['package_id'], resource_id=view['resource_id'], view_id=view['id'], **kwargs)


def collection_stats():
    """
    Get collection stats, grouped by collectionCode
    @return:
    """

    resource_id = config.get("ckanext.nhm.collection_resource_id")

    context = {'model': model, 'session': model.Session, 'user': c.user}

    sql = '''SELECT "collectionCode", COUNT(*) AS count
           FROM "{resource_id}"
           GROUP BY "collectionCode" ORDER BY count DESC'''.format(resource_id=resource_id)

    result = toolkit.get_action('datastore_search_sql')(context, {'sql': sql})
    total = 0

    collections = OrderedDict()

    for record in result['records']:
        # TEMP: After next run, this will not be needed
        if not record['collectionCode']:
            continue
        count = int(record['count'])
        collections[record['collectionCode']] = count
        total += count

    stats = {
        'total': total,
        'collections': collections
    }

    return stats


def get_department(collection_code):
    """
    Return a department name for collection code
    @param collection_code: BOT, PAL etc.,
    @return: Full department name - Entomology
    """

    # TODO: Update record to use this

    departments = {
        'BMNH(E)': 'Entomology',
        'BOT': 'Botany',
        'MIN': 'Mineralogy',
        'PAL': 'Paleontology',
        'ZOO': 'Zoology',
    }

    return departments[collection_code]

def delimit_number(num):
    """
    Separate long number into thousands 1000000 => 1,000,000
    @param num:
    @return:
    """
    return "{:,}".format(num)

def api_doc_link():
    return link_to(_('API Docs'), 'http://docs.nhm.apiary.io/')

