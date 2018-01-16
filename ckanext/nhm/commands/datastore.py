#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging

from ckanext.datastore.db import _get_engine

import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger()


class DatastoreCommand(toolkit.CkanCommand):
    '''Datastore commands, for modifying CKAN datastore resources
    
    Commands:
    
        purge-all - Delete all datasets and datastore tables
        paster datastore purge-all -c /etc/ckan/default/development.ini
    
        replace - Update datastore aliases
        paster datastore replace -i [resource_id] -t [table] -c /etc/ckan/default/development.ini
            Required param: ID of the datastore resource to update
            Required param: str alias

    '''
    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(DatastoreCommand, self).__init__(name)
        self.parser.add_option(u'-i', u'--resource-id',
                               help=u'Please enter the datastore resource ID to replace')
        self.parser.add_option(u'-t', u'--table',
                               help=u'Please enter the replacement table name')

    def command(self):
        '''Retrieves a method to execute based on input args.'''
        if not self.args or self.args[0] in [u'--help', u'-h', u'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        self.context = {u'user': u'admin'}

        # Set up datastore DB engine
        self.engine = _get_engine({
            u'connection_url': toolkit.config[u'ckan.datastore.write_url']
            })

        cmd = self.args[0]

        if cmd == u'replace':
            self.replace()
        elif cmd == u'purge-all':
            self.purge_all()
        else:
            print u'Command %s not recognized' % cmd

    def _get_datastore_or_fail(self, resource_id):
        '''Get the resource from the datastore - if not found, throw an exception.

        :param resource_id: the ID of the resource to try to retrieve

        '''
        data = {
            u'resource_id': resource_id, u'limit': 0
            }

        try:
            return toolkit.get_action(u'datastore_search')({}, data)
        except toolkit.ObjectNotFound:
            raise self.BadCommand(u'Datastore resource %s does not exist' % resource_id)

    def replace(self):
        '''Replace a datastore table with another table
        
        We do this if we're doing a full reload of the data
        
        Params: resource-id: the datastore resource to replace
                table: the table name to replace it with


        '''
        if not self.options.resource_id:
            msg = u'No resource id supplied'
            raise self.BadCommand(msg)

        if not self.options.table:
            msg = u'No table supplied'
            raise self.BadCommand(msg)

        # Load the existing resource to check it exists
        self._get_datastore_or_fail(self.options.table)

        # And check the new table exists
        self._get_datastore_or_fail(self.options.resource_id)

        response = self.ask(u'You are about to replace %s with table %s. '
                            u'Are you sure you want to continue?' % (
                                self.options.resource_id, self.options.table))

        # If user confirms the action, we're going to rename the tables
        # in a single transaction
        if response:

            # We don't just delete existing tables - we rename as *.bak
            backup_resource_id = u'{resource_id}-bak'.format(
                    resource_id=self.options.resource_id)

            # Make sure the backup table doesn't already exist
            # These need to be manually deleted after replacement
            if self.engine.dialect.has_table(self.engine.connect(), backup_resource_id):
                raise self.BadCommand(u'Backup resource table %s already exists. '
                                      u'Please delete before '
                                      u'running this operation.' % self.options.table)

            # We're going to perform the two rename operations in one transaction
            # so won't impact users
            connection = self.engine.connect()
            trans = connection.begin()
            try:
                # First rename the existing resource table - we'll keep it
                # as *-bak just in case
                connection.execute(u'ALTER TABLE "{resource_id}" '
                                   u'RENAME TO "{backup_resource_id}"'.format(
                        resource_id=self.options.resource_id,
                        backup_resource_id=backup_resource_id))
                connection.execute(
                        u'ALTER TABLE "{table}" RENAME TO "{resource_id}"'.format(
                                table=self.options.table,
                                resource_id=self.options.resource_id))
                trans.commit()
            except:
                trans.rollback()
                raise
            else:
                print u'SUCCESS: Resource %s replaced' % self.options.resource_id

    def purge_all(self):
        '''Remove all datasets and tables from the datastore.'''
        response = self.ask(
                u'You are about to remove all datasets and datastore tables. '
                u'Are you sure you want to continue?')

        # If user confirms the action, we're going to rename the tables
        # in a single transaction
        if response:

            pkgs = toolkit.get_action(u'current_package_list_with_resources')(
                    self.context, {})

            for pkg_dict in pkgs:
                for resource in pkg_dict[u'resources']:

                    try:
                        toolkit.get_action(u'datastore_delete')(self.context, {
                            u'resource_id': resource[u'id'], u'force': True
                            })
                    except toolkit.ObjectNotFound:
                        # Ignore missing datastore tables

                        # Load the package model and delete
                        pkg = model.Package.get(pkg_dict[u'id'])

                        if pkg:
                            rev = model.repo.new_revision()
                            pkg.purge()
                            model.repo.commit_and_remove()
                            print u'%s purged' % pkg_dict[u'name']
