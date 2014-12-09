
import logging
import pylons
import ckan.logic as logic
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
from sqlalchemy.exc import ProgrammingError

log = logging.getLogger()


class ResourceIndexCommand(CkanCommand):
    """
    Add btree indexes to

    Param: ID of the resource to update

    paster resource-index update-fulltext-index -i b21328c1-2b24-411a-9036-4da280d3eaac -c /etc/ckan/default/development.ini
    paster resource-index add-index -i de8f5572-cb5a-4e03-9f34-917cb25d2e89 -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    engine = None

    def __init__(self, name):

        super(ResourceIndexCommand, self).__init__(name)
        self.parser.add_option('-i', '--resource-id', help='Please enter the resource ID to update')

    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        cmd = self.args[0].replace('-', '_')

        if cmd.startswith('_'):
            print 'Cannot call private command %s' % cmd
            return

        self._load_config()

        # Set up database engine
        data_dict = {
            'connection_url': pylons.config['ckan.datastore.write_url']
        }

        self.engine = _get_engine(data_dict)

        data = {
            'resource_id': self.options.resource_id,
            'limit': 0
        }

        datastore = logic.get_action('datastore_search')({}, data)

        # Call the command method
        getattr(self, cmd)(datastore)

    def add_btree_index(self, datastore):
        """
        Loop through all fields in the datastore, and add a btree index
        @param datastore:
        @return:
        """

        print 'Adding btree indexes'

        for field in datastore.get('fields', []):
            # Ignore any special fields (including _id; that's already indexed)
            if field['id'].startswith('_'):
                continue

            idx = '_'.join([self.options.resource_id, field['id'], 'idx'])

            sql = 'CREATE INDEX "{idx}" ON "{resource_id}" ("{field}")'.format(
                idx=idx,
                resource_id=self.options.resource_id,
                field=field['id']
            )

            try:
                self.engine.execute(sql)
            except ProgrammingError, e:
                # Index already exists
                print e
            else:
                #  Success: index added
                print 'Added btree index to {resource_id}.{field}'.format(
                    resource_id=self.options.resource_id,
                    field=field['id']
                )

    def update_fulltext_index(self, datastore):
        """
        Collect all text and citext fields in a datastore, concatenate into an array
        Suitable for updating the _full_text index field.  This is used if a datastore
        Is updated via a CSV import - although isn't the recommended approach
        @param datastore:
        @return:
        """

        print 'Updating full text index'

        # Create list of text fields
        # They need to be wrapped in double quotes (field names; not literal value)
        text_fields = '","'.join([str(field['id']) for field in datastore.get('fields', []) if field['type'] in ['text', 'citext']])

        sql = u'UPDATE "{resource_id}" SET _full_text = to_tsvector(ARRAY_TO_STRING(ARRAY["{text_fields}"], \' \'))'.format(
            resource_id=self.options.resource_id,
            text_fields=text_fields
        )

        self.engine.execute(sql)

        print 'Updated full text index for resource %s' % self.options.resource_id
