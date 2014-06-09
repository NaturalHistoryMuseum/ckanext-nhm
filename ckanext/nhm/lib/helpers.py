
import logging
import json
import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import itertools
from ckanext.issues.model import Issue, ISSUE_STATUS
from sqlalchemy.orm import joinedload
from sqlalchemy import func

log = logging.getLogger(__name__)

NotFound = logic.NotFound

def get_site_statistics():
    #TEMP: Just to put some stats on the home page
    stats = {}
    stats['dataset_count'] = logic.get_action('package_search')(
        {}, {"rows": 1})['count']
    result = model.Session.execute(
        '''select count(*) from related r
           left join related_dataset rd on r.id = rd.related_id
           where rd.status = 'active' or rd.id is null''').first()[0]
    stats['related_count'] = result

    return stats


# def get_record_point(rec):
#
#     # TODO: What should happen if lat/lon not sane?
#     if rec['decimalLatitude'] and rec['decimalLongitude']:
#
#
#
#     return None


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


def form_select_datastore_field_options(resource_id=None, required=False):

    fields = []
    # Need to check for resource_id as this form gets loaded on add, nut just edit
    # And on add there will be no resource_id
    if resource_id:
        datastore_fields = get_datastore_fields(resource_id)
        # If this isn't required, add the None option
        if datastore_fields and not required:
            fields = list(itertools.chain([None], [{'value': f['id'], 'name': f['id']} for f in datastore_fields]))

    return fields


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