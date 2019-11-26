#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


import logging
import shutil

import os

from ckan.lib.uploader import ResourceUpload
from ckan.plugins import toolkit

log = logging.getLogger()


class FileCommand(toolkit.CkanCommand):
    '''Datastore commands, for modifying CKAN datastore resources

    :param resource_id: the datastore resource to replace
    :param file: the path to the file to replace it with
    
    Commands:
    
        replace-file - Replace an uploaded resource file with another
    
        If you have a file that is to big to upload, you can use this to
        replace a small dummy file with the large file.
    
        paster resource replace-file -c /etc/ckan/default/development.ini -f

    '''
    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def __init__(self, name):

        super(FileCommand, self).__init__(name)
        self.parser.add_option(u'-r', u'--resource-id',
                               help=u'Please enter the datastore resource ID to replace')
        self.parser.add_option(u'-p', u'--file-path',
                               help=u'Please enter the path to the replacement file')

    def command(self):
        '''Retrieves a method to execute based on input args.'''

        if not self.args or self.args[0] in [u'--help', u'-h', u'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        user = toolkit.get_action(u'get_site_user')({u'ignore_auth': True}, {})
        self.context = {u'user': user[u'name']}

        cmd = self.args[0]

        if cmd == u'replace':
            self.replace()
        else:
            print u'Command %s not recognized' % cmd

    def replace(self):
        '''Replace an uploaded resource file with another file.'''

        if not self.options.resource_id:
            msg = u'No resource id supplied'
            raise self.BadCommand(msg)

        if not self.options.file_path:
            msg = u'No file path supplied'
            raise self.BadCommand(msg)

        resource_id = self.options.resource_id
        fpath = self.options.file_path

        # Check file exists
        if not os.path.isfile(fpath):
            raise self.BadCommand(u'Replace file %s does not exist' % fpath)

        # Check resource exists
        data_dict = {
            u'id': resource_id
            }
        try:
            resource = toolkit.get_action(u'resource_show')(self.context, data_dict)
        except toolkit.ObjectNotFound:
            raise self.BadCommand(u'Resource ID %s does not exist' % resource_id)

        if resource.get(u'url_type') != u'upload':
            raise self.BadCommand(u'No resource files available')

        if resource.get(u'datastore_active', False):
            raise self.BadCommand(
                    u'Resource has an active datastore - cannot replace the file')

        # Get the file path
        upload = ResourceUpload(resource)
        resource_fpath = upload.get_path(resource[u'id'])

        # Back up the file to be overwritten
        resource_fname = os.path.basename(resource_fpath)
        shutil.copy(resource_fpath, os.path.join('/tmp', resource_fname))
        # And then overwrite the file
        shutil.copy(fpath, resource_fpath)

        print u'SUCCESS: The download file for resource %s has been replaced with %s' % (
            resource_id, fpath)
