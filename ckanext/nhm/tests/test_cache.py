#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import paste.fixture
import pylons.test
import pylons.config as config
import webtest

import ckan.model as model
import ckan.tests as tests
import ckan.plugins
import ckan.new_tests.factories as factories


class TestNHMCacheFunctions(object):
    '''Tests for the plugin_v5_custom_config_setting module.'''
    def _get_app(self, users_can_create_groups):
        '''

        :param users_can_create_groups: 

        '''

        # Return a test app with the custom config.
        app = ckan.config.middleware.make_app(config[u'global_conf'], **config)
        app = webtest.TestApp(app)

        # ckan.plugins.load('example_iauthfunctions_v5_custom_config_setting')

        return app

    def teardown(self):
        ''' '''

        # Delete any stuff that's been created in the db, so it doesn't
        # interfere with the next test.
        model.repo.rebuild_db()

    def test_dataset_search_is_cached(self):
        ''' '''
        app = self._get_app(users_can_create_groups=False)
        sysadmin = factories.Sysadmin()

        tests.call_action_api(app, u'group_create', name=u'test-group',
                              apikey=sysadmin[u'apikey'])
        pass



