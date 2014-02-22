import sys
import re
import ckan.model as model
import ckan.logic as logic
import ckan.lib.cli as cli
import ckan
import os

import ConfigParser
import yaml

import sqlalchemy
from sqlalchemy.exc import ProgrammingError
import pylons
import logging
from datetime import datetime
from ckanext.datastore.db import _get_engine
from ke2sql import config as ke2sql_config

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

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print KEEMuCommand.__doc__
            return

        self._load_config()

        cmd = self.args[0]

        if cmd == 'build-dataset':
            self.build_dataset()
            if self.verbose:
                print 'Building KE EMu datasets: SUCCESS'
        else:
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return

    def build_dataset(self):
        """
        Using the KE EMu source table

        Known issues:
        KE EMu datastore should be at the same point
        """

        # Load the dataset definitions
        f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'datasets.yaml'))
        datasets = yaml.safe_load(f)

        keemu_schema = ke2sql_config.get('database', 'schema')
        keemu_dataset_name = pylons.config['nhm.keemu_dataset_name']

        engine = _get_engine({'connection_url': pylons.config['ckan.datastore.write_url']})

        # Set up API context
        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}

        try:

            # Try and load the KE EMu package
            package = logic.get_action('package_show')(context, {'id': keemu_dataset_name})

        except logic.NotFound:

            # KE EMu package not found; create it

            # Error adds dataset_show to __auth_audit: remove it
            context['__auth_audit'] = []

            # TODO: More metadata. Create date etc.,
            # TODO: Read file produced date

            package_params = {
                'author': None,
                'author_email': None,
                'license_id': u'other-open',
                'maintainer': None,
                'maintainer_email': None,
                'name': keemu_dataset_name,
                'notes': u'Specimen records from the Natural History Museum\'s catalogue',
                'resources': [],
                'title': "Specimen catalogue",
            }

            try:
                # Create the dataset
                package = logic.get_action('package_create')(context, package_params)
            except Exception:
                raise

        except ProgrammingError, e:
            raise

        # Build a temporary table of determinations, which uses part's parents

        # Drop and create
        engine.execute(sqlalchemy.text('DROP TABLE IF EXISTS tmp_determination'.format(schema=keemu_schema)))
        engine.execute(sqlalchemy.text("""CREATE TEMP TABLE tmp_determination
                                             AS
                                                (SELECT DISTINCT ON(d.specimen_irn) specimen_irn, taxonomy_irn
                                                FROM {schema}.determination d
                                                INNER JOIN {schema}.specimen s ON s.irn = d.specimen_irn ORDER BY d.specimen_irn, filed_as DESC)
                                             UNION
                                                (SELECT DISTINCT ON(s.irn) s.irn as specimen_irn, taxonomy_irn
                                                FROM {schema}.SPECIMEN s
                                                INNER JOIN {schema}.part p ON p.irn = s.irn
                                                INNER JOIN {schema}.determination d ON p.parent_irn = d.specimen_irn
                                                WHERE NOT EXISTS (SELECT 1 FROM {schema}.determination WHERE specimen_irn = s.irn)
                                                ORDER BY s.irn, filed_as DESC)
                                        """.format(schema=keemu_schema)))

        # Get all existing resources keyed by name
        existing_datasets = {r['name']: r for r in package['resources']}

        for name, dataset in datasets.items():

            sys.stdout.write('Rebuilding dataset %s:' % name)
            sys.stdout.flush()

            try:

                resource_id = existing_datasets[name]['id']

            except KeyError:  # We don't have a datastore resource so create one

                log.info('Creating datastore %s.' % name)

                datastore_params = {
                    'records': [],
                    'resource': {
                        'package_id': package['id'],
                        'name': name,
                        'description': dataset['description'],
                    }
                }

                datastore = logic.get_action('datastore_create')(context, datastore_params)
                resource_id = datastore['resource_id']

            else:

                # Resource already exists - need to update last modified date
                resource = existing_datasets[name]
                resource['last_modified'] = datetime.now()
                logic.get_action('resource_update')(context, resource)

            finally:

                # Delete & recreate the tables, building them from the ME EMu source tables

                # Delete the existing table (in the datastore)
                engine.execute(sqlalchemy.text(u'DROP TABLE IF EXISTS "%s"' % resource_id))

                # And recreate the table
                select_sql = dataset['sql'].format(schema=keemu_schema)
                create_sql = sqlalchemy.text('CREATE TABLE "{id}" AS {select_sql}'.format(id=resource_id, select_sql=select_sql))
                engine.execute(create_sql)

                # Hacky fix for adding _full_text column
                # TODO: Either integrate this properly, or use API when DwC has been implemented
                engine.execute(u'ALTER TABLE "{id}" ADD COLUMN _full_text tsvector'.format(id=resource_id))

                # Get all text fields
                text_columns = engine.execute(sqlalchemy.text(u'SELECT STRING_AGG(QUOTE_IDENT(column_name), \', \') FROM information_schema.columns WHERE table_name = \'{id}\' and data_type = \'character varying\''.format(id=resource_id))).scalar()

                # Populate _full_text with all text fields
                engine.execute(sqlalchemy.text(u'UPDATE "{id}" set _full_text = to_tsvector(ARRAY_TO_STRING(ARRAY[{text_columns}], \' \'))'.format(id=resource_id, text_columns=text_columns)))

                print ' SUCCESS'
