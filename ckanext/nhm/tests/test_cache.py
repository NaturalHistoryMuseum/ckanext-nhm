#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json

from ckan.tests import factories, helpers


class TestNHMCacheFunctions(helpers.FunctionalTestBase):
    '''Tests for the plugin_v5_custom_config_setting module.'''

    def test_dataset_search_is_cached(self):
        ''' '''
        sysadmin = factories.Sysadmin()

        auth = {u'Authorization': sysadmin[u'apikey']}
        params = {u'name': u'test-group'}
        response = self._test_app.post(u'/api/action/group_create', params=params,
                                       extra_environ=auth)
        assert json.loads(response.body)['success'] is True
