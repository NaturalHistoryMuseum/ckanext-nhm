
import logging
import pylons
import ckan.logic as logic
from ckan.plugins import toolkit as tk
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
from sqlalchemy.exc import ProgrammingError

log = logging.getLogger()

class DatastoreCommand(CkanCommand):
    """

    Datastore commands, for modifying CKAN datastore resources

    Commands:

        purge-all - Delete all datasets and datastore tables
        paster datastore purge-all -c /etc/ckan/default/development.ini

        alias - Update datastore aliases
        paster datastore alias [resource_id] [str alias] -c /etc/ckan/default/development.ini
            Required param: ID of the datastore resource to update
            Required param: str alias

        update-stats - Update datastore stats
        paster datastore update-stats -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):

        super(DatastoreCommand, self).__init__(name)
        self.parser.add_option('-i', '--resource-id', help='Please enter the datastore resource ID to replace')
        self.parser.add_option('-t', '--table', help='Please enter the replacement table name')

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        user = tk.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        # Set up datastore DB engine
        self.engine = _get_engine({
            'connection_url': pylons.config['ckan.datastore.write_url']
        })

        cmd = self.args[0]

        if cmd == 'replace':
            self.replace()
        elif cmd == 'purge-all':
            self.purge_all()
        else:
            print 'Command %s not recognized' % cmd

    def replace(self):
        """
        Replace a datastore table with another table

        We do this if we're doing a full reload of the data

        Params: resource-id: the datastore resource to replace
                table: the table name to replace it with

        @return:
        """

        if not self.options.resource_id:
            msg = 'No resource id supplied'
            raise self.BadCommand(msg)

        if not self.options.table:
            msg = 'No table supplied'
            raise self.BadCommand(msg)

        # Load the existing resource to check it exists

        data = {
            'resource_id': self.options.resource_id,
            'limit': 0
        }

        try:
            logic.get_action('datastore_search')({}, data)
        except logic.NotFound:
            raise self.BadCommand('Datastore resource %s to replace does not exist' % self.options.resource_id)


        # And check the new table exists
        data = {
            'resource_id': self.options.table,
            'limit': 0
        }

        try:
            logic.get_action('datastore_search')({}, data)
        except logic.NotFound:
            raise self.BadCommand('Replacement table %s does not exist' % self.options.table)

        response = self.ask('You are about to replace %s with table %s. Are you sure you want to continue?' % (
            self.options.resource_id, self.options.table)
        )

        # If user confirms the action, we're going to rename the tables in a single transaction
        if response:

            # We don't just delete existing tables - we rename as *.bak
            backup_resource_id = '{resource_id}-bak'.format(
                resource_id=self.options.resource_id
            )

            # Make sure the backup table doesn't already exist
            # These need to be manually deleted after replacement
            if self.engine.dialect.has_table(self.engine.connect(), backup_resource_id):
                raise self.BadCommand('Backup resource table %s already exists. Please delete before running this operation.' % self.options.table)

            # We're going to perform the two rename operations in one transaction so won't impact users
            connection = self.engine.connect()
            trans = connection.begin()
            try:




                # First rename the existing resource table - we'll keep it as *-bak just in case
                # connection.execute('ALTER TABLE "{resource_id}" RENAME TO "{resource_id}-bak"'.format(
                #     resource_id=self.options.resource_id
                # ))
                # connection.execute('ALTER TABLE "%s" RENAME TO "%s-bak"')
                trans.commit()
            except:
                trans.rollback()
                raise




        # print self.parser
        # print type(self.parser)
        #
        # print self.parser.get_option('-i')
        #
        # resource_id = self.options.resource_id
        #
        # assert resource_id != None
        #
        # print resource_id
        # print 'ALIAS'

    def purge_all(self):



        print 'PURGE'
