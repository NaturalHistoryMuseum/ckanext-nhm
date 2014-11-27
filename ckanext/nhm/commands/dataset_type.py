
import logging
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY

# Dataset type to be automatically added to the vocabulary
DEFAULT_DATASET_TYPES = ['Collections', 'Library and archives']


class DatasetTypeCommand(CkanCommand):
    """
    Create / Add / Delete type from the dataset type vocabulary

    Commands:
        paster dataset-type create-vocabulary -c <config>
        paster dataset-type create-vocabulary -c /vagrant/etc/default/development.ini
        paster dataset-type create-vocabulary -c /etc/ckan/default/development.ini

        paster dataset-type create-type string -c /vagrant/etc/default/development.ini

    Where:
        <config> = path to your ckan config file

    The commands should be run from the ckanext-nhm directory.

    """
    summary = __doc__.strip().split('\n')[0]
    usage = '\n' + __doc__
    context = None

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        cmd = self.args[0].replace('-', '_')

        if cmd.startswith('_'):
            print 'Cannot call private command %s' % cmd
            return

        self._load_config()

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        # Call the command method
        getattr(self, cmd)()

    def create_vocabulary(self):

        try:
            data = {'id': DATASET_TYPE_VOCABULARY}
            toolkit.get_action('vocabulary_show')(self.context, data)
            print("Dataset category vocabulary already exists, skipping.")

        except toolkit.ObjectNotFound:

            print "Creating vocab '{0}'".format(DATASET_TYPE_VOCABULARY)
            data = {'name': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_create')(self.context, data)

            for dataset_type in (DEFAULT_DATASET_TYPES):
                self.add_type(vocabulary['id'], dataset_type)

    def add_type(self, vocabulary_id, dataset_type):
        print "Adding tag {0} to vocab '{1}'".format(dataset_type, DATASET_TYPE_VOCABULARY)
        data = {'name': dataset_type, 'vocabulary_id': vocabulary_id}
        toolkit.get_action('tag_create')(self.context, data)

    def create_type(self):

        try:
            dataset_type = self.args[1]
        except IndexError:
            print 'Please specify the type to add'
        else:
            data = {'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)
            self.add_type(vocabulary['id'], dataset_type)

    def delete_type(self):

        try:
            dataset_type = self.args[1]
        except IndexError:
            print 'Please specify the type to delete'
        else:
            data = {'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)
            data = {'name': dataset_type, 'vocabulary_id': vocabulary['id']}
            toolkit.get_action('tag_delete')(self.context, data)