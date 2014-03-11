import ckan.lib.cli as cli
import logging
from ckanext.nhm.lib.keemu import KeEMuDatastore

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
    context = None

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print KEEMuCommand.__doc__
            return

        self._load_config()

        cmd = self.args[0]

        if cmd in ['create-datasets', 'update-datasets']:

            #  Method to run on the datastore cls - create or update
            method = cmd.replace('-datasets', '')

            for cls in KeEMuDatastore.__subclasses__():
                datastore = cls()
                getattr(datastore, method)()
        else:
            print 'Command "%s" not recognized' % (cmd,)
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return



