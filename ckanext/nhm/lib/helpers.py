
import logging
import json
import ckan.model as model
import ckan.logic as logic

log = logging.getLogger(__name__)

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

def get_record_point(rec):

    # TODO: What should happen if lat/lon not sane?
    if rec['decimalLatitude'] and rec['decimalLongitude']:

        return json.dumps({
            'type': 'Point',
            'coordinates': [rec['decimalLongitude'], rec['decimalLatitude']]
        })

    return None

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