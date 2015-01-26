
import logging
from ckan.lib.cli import CkanCommand
from ckan.plugins import toolkit

log = logging.getLogger()


class DatasetPurgeAllCommand(CkanCommand):
    """
    Add btree indexes to

    Param: ID of the resource to update

    paster dataset-purge-all -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        return

        # self._load_config()
        #
        # # Set up context
        # user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        # self.context = {'user': user['name']}
        #

        #
        # import ckan.model as model
        #
        # package_names = toolkit.get_action('package_list')(self.context, {})
        #
        # print '%i packages to purge' % len(package_names)
        #
        # for package_name in package_names:
        #
        #     # Load the package and loop through the resources
        #     pkg_dict = toolkit.get_action('package_show')(self.context, {'id': package_name})
        #     for resource in pkg_dict['resources']:
        #         # Does this have an activate datastore table?
        #         if resource['datastore_active']:
        #
        #             print 'Deleting datastore %s' % resource['id']
        #             toolkit.get_action('datastore_delete')(self.context, {'resource_id': resource['id'], 'force': True})
        #
        #     # Load the package model and delete
        #     pkg = model.Package.get(pkg_dict['id'])
        #
        #     rev = model.repo.new_revision()
        #     pkg.purge()
        #     model.repo.commit_and_remove()
        #     print '%s purged' % pkg_dict['name']
