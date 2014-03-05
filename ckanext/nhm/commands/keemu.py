import ckan.model as model
import ckan.logic as logic
import ckan.lib.cli as cli
import pylons
import logging
from ckanext.nhm.lib.keemu import keemu_datastore_create_table

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

        if cmd in ['create-dataset', 'update-dataset']:

            f = cmd.replace('-', '_')
            result = getattr(self, f)()

            if self.verbose:
                print result

        else:
            print 'Command "%s" not recognized' % (cmd,)
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return

    def create_dataset(self):

        """
        Initiate the KE EMu dataset - creating the dataset and copying the KE EMu data into it
        """

        # Set up API context
        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}
        keemu_dataset_name = pylons.config['nhm.keemu_dataset_name']

        # FIXME: Temp
        import random
        import string

        char_set = string.ascii_lowercase + string.digits
        keemu_dataset_name = ''.join(random.sample(char_set*6, 6))

        # For the initial dataset
        try:

            # Try and load the KE EMu package
            package = logic.get_action('package_show')(context, {'id': keemu_dataset_name})
            # If package already exists, skip
            return 'KE EMu dataset already exists: SKIPPING'

        except logic.NotFound:

            # KE EMu package not found; create it

            # Error adds dataset_show to __auth_audit: remove it
            context['__auth_audit'] = []

            package_params = {
                'author': None,
                'author_email': None,
                'license_id': u'other-open',
                'name': keemu_dataset_name,
                'maintainer': None,
                'maintainer_email': None,
                'notes': u'Specimen records from the Natural History Museum\'s collection',
                'resources': [],
                'title': "Specimen catalogue",
            }

            # Try to create the dataset
            package = logic.get_action('package_create')(context, package_params)

            # Create the datastore
            datastore_params = {
                'records': [],
                'resource': {
                    'package_id': package['id'],
                    'name': 'Collection',
                    'description': 'Collection',
                }
            }

            #  Try to create the datastore (this method associates a datastore table directly with a dataset
            datastore = logic.get_action('datastore_create')(context, datastore_params)

            # And create the datastore table
            keemu_datastore_create_table(datastore['resource_id'])

            print datastore['resource_id']


        return 'Creating KE EMu dataset: SUCCESS'


    def update_dataset(self):
        """
        KE EMu update has run - update the CKAN dataset
        """
        # TODO: Can we update using the API?
        # TODO: Deletes?
        pass
