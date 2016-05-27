
import os
import shutil
import logging
import ckan.logic as logic
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand
import ckan.lib.uploader as uploader

log = logging.getLogger()

class FileCommand(CkanCommand):
    """

    Datastore commands, for modifying CKAN datastore resources

    Commands:

        replace-file - Replace an uploaded resource file with another

        If you have a file that is to big to upload, you can use this to
        replace a small dummy file with the large file.

        paster resource replace-file -c /etc/ckan/default/development.ini -f


    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):

        super(FileCommand, self).__init__(name)
        self.parser.add_option('-r', '--resource-id', help='Please enter the datastore resource ID to replace')
        self.parser.add_option('-p', '--file-path', help='Please enter the path to the replacement file')

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        cmd = self.args[0]

        if cmd == 'replace':
            self.replace()
        else:
            print 'Command %s not recognized' % cmd

    def replace(self):
        """
        Replace an uploaded resource file with another file

        Params: resource-id: the datastore resource to replace
                file: the path to the file to replace it with

        @return:
        """

        if not self.options.resource_id:
            msg = 'No resource id supplied'
            raise self.BadCommand(msg)

        if not self.options.file_path:
            msg = 'No file path supplied'
            raise self.BadCommand(msg)

        resource_id = self.options.resource_id
        fpath = self.options.file_path

        # Check file exists
        if not os.path.isfile(fpath):
            raise self.BadCommand('Replace file %s does not exist' % fpath)

        # Check resource exists
        data_dict = {
            'id': resource_id
        }
        try:
            resource = toolkit.get_action('resource_show')(self.context, data_dict)
        except logic.NotFound:
            raise self.BadCommand('Resource ID %s does not exist' % resource_id)

        if resource.get('url_type') != 'upload':
            raise self.BadCommand('No resource files available')

        if resource.get('datastore_active', False):
            raise self.BadCommand('Resource has an active datastore - cannot replace the file')

        # Get the file path
        upload = uploader.ResourceUpload(resource)
        resource_fpath = upload.get_path(resource['id'])

        # Back up the file to be overwritten
        resource_fname = os.path.basename(resource_fpath)
        shutil.copy(resource_fpath, os.path.join('/tmp', resource_fname))
        # And then overwrite the file
        shutil.copy(fpath, resource_fpath)

        print 'SUCCESS: The download file for resource %s has been replaced with %s' % (resource_id, fpath)