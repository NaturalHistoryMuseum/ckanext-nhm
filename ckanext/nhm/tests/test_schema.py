from nose.tools import assert_raises

import ckan.logic as logic

import ckan.plugins as p
import ckan.new_tests.factories as factories
import ckan.new_tests.helpers as helpers

from ckanext.nhm.tests.factories import Vocabulary


class TestNHMSchemaFunctions(object):
    '''
    Tests for the plugin_v5_custom_config_setting module.
    '''

    @classmethod
    def setup_class(cls):
        p.load('nhm')

    @classmethod
    def teardown_class(cls):
        p.unload('nhm')
        helpers.reset_db()

    def test_dataset_cannot_be_created_without_notes(self):
        user = factories.User()

        context = {
            'user': user,
        }

        data = {
            'name': 'crimeandpunishment',
            'owner_org': 'test_org_2',

            # 'package_type':
        }

        assert_raises(logic.ValidationError, logic.get_action('package_create')(context, data))

        # # # Create the resource & datastore
        # data = {
        #     'resource': {
        #         'package_id': package['id'],
        #         'name': 'Test records'
        #     },
        #     'fields': [{'id': 'book', 'type': 'text'},
        #                {'id': 'author', 'type': 'text'}],
        #     'records': [
        #         {'book': 'annakarenina', 'author': 'tolstoy'}
        #     ]
        # }
        # result = helpers.call_action('datastore_create', **data)
        #
        # record_data = {
        #     'resource_id': result['resource_id'],
        #     'record_id': 1
        # }
        # # Retrieve the record
        # record = helpers.call_action('record_show', **record_data)
        # # Ensure the _id of the retrieved record is the same as the one supplied
        # assert_equal(record['data']['_id'], record_data['record_id'])
