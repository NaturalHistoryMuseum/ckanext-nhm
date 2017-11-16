from nose.tools import assert_equal

import ckan.plugins as p
import ckan.new_tests.factories as factories
import ckan.new_tests.helpers as helpers

from ckanext.nhm.tests.factories import Vocabulary


class TestNHMRecordFunctions(object):
    '''
    Tests for the plugin_v5_custom_config_setting module.
    '''

    @classmethod
    def setup_class(cls):
        p.load('datastore')
        p.load('nhm')

    @classmethod
    def teardown_class(cls):
        p.unload('datastore')
        p.unload('nhm')
        helpers.reset_db()

    def test_datastore_dataset_has_viewable_records(self):
        # Create vocabulary
        Vocabulary()
        # Create the package
        package = factories.Dataset(
            notes='blah blah',
            dataset_category='tag1',
            author='Test'
        )
        # Create the resource & datastore
        data = {
            'resource': {
                'package_id': package['id'],
                'name': 'Test records'
            },
            'fields': [{'id': 'book', 'type': 'text'},
                       {'id': 'author', 'type': 'text'}],
            'records': [
                {'book': 'annakarenina', 'author': 'tolstoy'}
            ]
        }
        result = helpers.call_action('datastore_create', **data)

        record_data = {
            'resource_id': result['resource_id'],
            'record_id': 1
        }
        # Retrieve the record
        record = helpers.call_action('record_show', **record_data)
        # Ensure the _id of the retrieved record is the same as the one supplied
        assert_equal(record['data']['_id'], record_data['record_id'])
