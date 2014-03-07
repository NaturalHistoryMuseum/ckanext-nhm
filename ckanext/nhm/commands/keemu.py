import ckan.model as model
import ckan.logic as logic
import ckan.lib.cli as cli
import pylons
import logging
from ckanext.nhm.lib.keemu import keemu_init_collection_datastore, keemu_init_artefacts_datastore
from itertools import chain
import sys

log = logging.getLogger(__name__)

class KEEMuCommand(cli.CkanCommand):
    '''
    Commands:
        paster --plugin=ckanext-nhm keemu build-dataset -c /etc/ckan/default/development.ini

    Where:
        <config> = path to your ckan config file

    The commands should be run from the ckanext-nhm directory.
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print KEEMuCommand.__doc__
            return

        self._load_config()

        cmd = self.args[0]
        func = cmd.replace('-', '_')

        if not func.startswith('_') and hasattr(self, func):
            getattr(self, func)()
        else:
            print 'Command "%s" not recognized' % (cmd,)
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return

    def _setup_datastore(self, package_params, resource_params):
        """
        Setup the CKAN datastore
        Return the datastore_resource_id
        """
        # Set up API context
        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}

        default_package_params = {
            'author': None,
            'author_email': None,
            'license_id': u'other-open',
            'maintainer': None,
            'maintainer_email': None,
            'resources': [],
        }

        #  Merge package params with default params
        package_params = dict(chain(default_package_params.iteritems(), package_params.iteritems()))

        try:

            # Try and load the KE EMu package
            package = logic.get_action('package_show')(context, {'id': package_params['name']})
            datastore_resource_id = package['resources'][0]['id']

        except logic.NotFound:

            # KE EMu package not found; create it
            # Error adds dataset_show to __auth_audit: remove it
            context['__auth_audit'] = []
            package = logic.get_action('package_create')(context, package_params)

            resource_params['package_id'] = package['id']

            datastore_params = {
                'records': [],
                'resource': resource_params
            }

            datastore = logic.get_action('datastore_create')(context, datastore_params)
            datastore_resource_id = datastore['resource_id']

        return datastore_resource_id

    def init_collection_dataset(self):

        """
        Initiate the KE EMu datasets - creating the dataset and copying the KE EMu data into it
        """

        # TODO: We need copy for this
        package_params = {
            'name': pylons.config['nhm.keemu_dataset_name'] + '4',
            'notes': u'Specimen records from the Natural History Museum\'s collection',
            'title': "Collection"
        }

        resource_params = {
            'name': 'Collection',
            'description': 'Collection',
        }

        dataset_resource_id = self._setup_datastore(package_params, resource_params)

        print 'Using dataset resource: %s' % dataset_resource_id

        keemu_init_collection_datastore(dataset_resource_id)

        print 'Created KE EMu collection dataset: SUCCESS'

    def init_artefact_dataset(self):

        """
        Initiate the KE EMu datasets - creating the dataset and copying the KE EMu data into it
        """

        # TODO: We need copy for this
        package_params = {
            'name': 'nhm-artefacts',
            'notes': u'Artefacts from the Natural History Museum\'s collection',
            'title': "Artefacts"
        }

        resource_params = {
            'name': 'Artefacts',
            'description': 'Artefacts',
        }

        dataset_resource_id = self._setup_datastore(package_params, resource_params)

        print 'Using dataset resource: %s' % dataset_resource_id

        keemu_init_artefacts_datastore(dataset_resource_id)

        print 'Created KE EMu artefact dataset: SUCCESS'

    def update_collection_dataset(self):
        """
        KE EMu update has run - update the CKAN dataset
        """
        # TODO: Can we update using the API?
        # TODO: Deletes?
        pass
