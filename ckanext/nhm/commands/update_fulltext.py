
import logging
import pylons
import ckan.logic as logic
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine

log = logging.getLogger()


class UpdateFullTextCommand(CkanCommand):
    """
    Update full text indexes
    Param: ID of the resource to update

    paster update-fulltext -i b21328c1-2b24-411a-9036-4da280d3eaac -c /vagrant/etc/default/development.ini
    paster update-fulltext -i de8f5572-cb5a-4e03-9f34-917cb25d2e89 -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    # Fields not to index
    blacklist = [
        'relatedResourceID',
        'relationshipOfResource',
        'associatedMedia',
        'registeredWeightUnit',
        'basisOfRecord',
        'modified',
        'created',
        'scientificNameAuthorship'
    ]

    def __init__(self, name):
        super(UpdateFullTextCommand, self).__init__(name)
        self.parser.add_option('-i', '--resource-id', help='Please enter the resource ID to update')

    def command(self):

        print 'Updating full text index'

        # Create the tables
        self._load_config()

        data = {
            'resource_id': self.options.resource_id,
            'limit': 0
        }

        result = logic.get_action('datastore_search')({}, data)

        # Create list of text fields
        # They need to be wrapped in double quotes (field names; not literal value)
        text_fields = '","'.join([str(field['id']) for field in result.get('fields', []) if field['type'] in ['text', 'citext'] and field['id'] not in self.blacklist])

        sql = u'UPDATE "{resource_id}" SET _full_text = to_tsvector(ARRAY_TO_STRING(ARRAY["{text_fields}"], \' \'))'.format(
            resource_id=self.options.resource_id,
            text_fields=text_fields
        )

        data_dict = {
            'connection_url': pylons.config['ckan.datastore.write_url']
        }

        _get_engine(data_dict).execute(sql)

        print 'Updated full text index for resource %s' % self.options.resource_id