
import logging
from ckan.plugins import toolkit
import ckan.model as model
from ckan.lib.cli import CkanCommand
from ckanext.nhm.model.stats import DatastoreStats

log = logging.getLogger()

class StatsCommand(CkanCommand):
    """
    Every time this command is run, the datastore_stats table is updated with record counts from the datastore
    Needs to run from there - rather than on resource update - as datapusher won't have added records to the datastore

    paster --plugin=ckanext-nhm stats  -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):

        print 'Updating stats'

        # Update datastore

        self._load_config()

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}

        data_dict = {
            'sql': "SELECT name FROM _table_metadata WHERE alias_of IS NULL"
        }

        datastore_resources = toolkit.get_action('datastore_search_sql')(context, data_dict)

        # Get a list of all resource ids
        q = model.Session.query(model.Resource.id).all()
        resource_ids = zip(*q)[0]

        for datastore_resource in datastore_resources['records']:

            # Ensure the name we have is a resource
            if unicode(datastore_resource['name']) in resource_ids:

                # Count the number of records
                data_dict = {
                    'sql': 'SELECT COUNT(*) FROM "%s"' % datastore_resource['name']
                }

                result = toolkit.get_action('datastore_search_sql')(context, data_dict)
                count = result['records'][0]['count']

                stats = DatastoreStats(count=count, resource_id=datastore_resource['name'])

                model.Session.add(stats)

        model.Session.commit()

        print 'Stats updated'