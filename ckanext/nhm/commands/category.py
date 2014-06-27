
import logging
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
from ckanext.nhm.logic.schema import DATASET_CATEGORY

log = logging.getLogger()
# TODO: Add logging settings

class CategoryCommand(CkanCommand):
    """
    Create / Add / Delete terms from the dataset category vocabulary

    Commands:
        paster category create -c <config>
        paster category create -c /vagrant/etc/default/development.ini

        paster category add-term string -c /vagrant/etc/default/development.ini

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

    def create(self):

        try:
            data = {'id': DATASET_CATEGORY}
            toolkit.get_action('vocabulary_show')(self.context, data)
            print("Dataset category vocabulary already exists, skipping.")

        except toolkit.ObjectNotFound:

            print "Creating vocab '{0}'".format(DATASET_CATEGORY)
            data = {'name': DATASET_CATEGORY}
            vocabulary = toolkit.get_action('vocabulary_create')(self.context, data)

            for term in (u'specimen', 'another'):
                self._add_term(vocabulary['id'], term)

    def _add_term(self, vocabulary_id, term):
        print "Adding tag {0} to vocab '{1}'".format(term, DATASET_CATEGORY)
        data = {'name': term, 'vocabulary_id': vocabulary_id}
        toolkit.get_action('tag_create')(self.context, data)

    def add_term(self):

        try:
            term = self.args[1]
        except IndexError:
            print 'Please specify the term to add'
        else:
            data = {'id': DATASET_CATEGORY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)
            self._add_term(vocabulary['id'], term)

    def delete_term(self):

        try:
            term = self.args[1]
        except IndexError:
            print 'Please specify the term to delete'
        else:
            data = {'id': DATASET_CATEGORY}
            vocabulary = toolkit.get_action('vocabulary_show')(self.context, data)
            data = {'name': term, 'vocabulary_id': vocabulary['id']}
            toolkit.get_action('tag_delete')(self.context, data)