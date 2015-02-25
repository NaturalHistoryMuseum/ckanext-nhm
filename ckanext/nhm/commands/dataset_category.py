
import logging
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY

# Dataset type to be automatically added to the vocabulary
DEFAULT_DATASET_CATEGORIES = [
    'Collections',
    'Corporate',
    'Library and archives',
    'Public engagement',
    'Research',
    'Citizen science'
]

class DatasetCategoryCommand(CkanCommand):
    """
    Create / Add / Delete type from the dataset type vocabulary

    Commands:
        paster dataset-category create-vocabulary -c <config>
        paster dataset-category create-vocabulary -c /etc/ckan/default/development.ini

        paster --plugin=ckanext-nhm dataset-type create-type 'Citizen Science' -c /etc/ckan/default/development.ini
        paster dataset-category delete-type specimen -c /etc/ckan/default/development.ini



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

        self._load_config()

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        cmd = self.args[0]

        if cmd == 'create-vocabulary':
            self.create_vocabulary()
        elif cmd == 'add-category':
            self.add_category()
        elif cmd == 'delete-category':
            self.delete_category()
        else:
            print 'Command %s not recognized' % cmd

    def create_vocabulary(self):
        """
        Create the dataset vocabulary

        paster dataset-category create-vocabulary -c /etc/ckan/default/development.ini

        @return:
        """

        try:
            data = {'id': DATASET_TYPE_VOCABULARY}
            toolkit.get_action('vocabulary_show')(self.context, data)
            print("Dataset category vocabulary already exists, skipping.")

        except toolkit.ObjectNotFound:

            print "Creating vocab '{0}'".format(DATASET_TYPE_VOCABULARY)
            data = {'name': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_create')(self.context, data)

            for category in DEFAULT_DATASET_CATEGORIES:
                self._add_tag(vocabulary['id'], category)

    def add_category(self):
        """
        Add a category to the dataset categories

        paster --plugin=ckanext-nhm dataset-category add-category 'Citizen Science 2' -c /etc/ckan/default/development.ini

        @return:
        """
        try:
            term = self.args[1]
        except IndexError:
            print 'Please specify the type to add'
        else:
            data = {'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)
            self._add_tag(vocabulary['id'], term)

    def delete_category(self):
        """
        Delete a category from the dataset categories

        paster --plugin=ckanext-nhm dataset-category delete-category specimen -c /etc/ckan/default/development.ini

        @return:
        """

        try:
            term = self.args[1]
        except IndexError:
            print 'Please specify the type to delete'
        else:
            data = {'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)

            for tag in vocabulary['tags']:
                if tag['display_name'] == term:
                    print 'Deleting term %s in vocabulary %s' % (tag['id'], vocabulary['id'])
                    data = {'id': tag['id'], 'vocabulary_id': vocabulary['id']}
                    toolkit.get_action('tag_delete')(self.context, data)
                    break

    def _add_tag(self, vocabulary_id, tag):
        print "Adding tag {0} to vocab '{1}'".format(tag, DATASET_TYPE_VOCABULARY)
        data = {'name': tag, 'vocabulary_id': vocabulary_id}
        toolkit.get_action('tag_create')(self.context, data)