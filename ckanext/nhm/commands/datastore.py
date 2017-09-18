
import logging
import pylons
import ckan.logic as logic
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
import ckan.model as model

log = logging.getLogger()

class DatastoreCommand(CkanCommand):
    """

    Datastore commands, for modifying CKAN datastore resources

    Commands:

        purge-all - Delete all datasets and datastore tables
        paster datastore purge-all -c /etc/ckan/default/development.ini

        replace - Update datastore aliases
        paster datastore replace -i [resource_id] -t [table] -c /etc/ckan/default/development.ini
            Required param: ID of the datastore resource to update
            Required param: str alias

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
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': 'admin'}

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

    def _get_datastore_or_fail(self, resource_id):

        data = {
            'resource_id': resource_id,
            'limit': 0
        }

        try:
            return toolkit.get_action('datastore_search')({}, data)
        except logic.NotFound:
            raise self.BadCommand('Datastore resource %s does not exist' % resource_id)

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
        self._get_datastore_or_fail(self.options.table)

        # And check the new table exists
        self._get_datastore_or_fail(self.options.resource_id)


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
                connection.execute('ALTER TABLE "{resource_id}" RENAME TO "{backup_resource_id}"'.format(
                    resource_id=self.options.resource_id,
                    backup_resource_id=backup_resource_id
                ))
                connection.execute('ALTER TABLE "{table}" RENAME TO "{resource_id}"'.format(
                    table=self.options.table,
                    resource_id=self.options.resource_id
                ))
                trans.commit()
            except:
                trans.rollback()
                raise
            else:
                print 'SUCCESS: Resource %s replaced' % self.options.resource_id

    def purge_all(self):

        response = self.ask(
            'You are about to remove all datasets and datastore tables. Are you sure you want to continue?'
        )

        # If user confirms the action, we're going to rename the tables in a single transaction
        if response:

            pkgs = toolkit.get_action('current_package_list_with_resources')(self.context, {})

            for pkg_dict in pkgs:
                for resource in pkg_dict['resources']:

                    try:
                        toolkit.get_action('datastore_delete')(self.context, {'resource_id': resource['id'], 'force': True})
                    except logic.NotFound:
                        # Ignore missing datastore tables

                        # Load the package model and delete
                        pkg = model.Package.get(pkg_dict['id'])

                        if pkg:
                            rev = model.repo.new_revision()
                            pkg.purge()
                            model.repo.commit_and_remove()
                            print '%s purged' % pkg_dict['name']