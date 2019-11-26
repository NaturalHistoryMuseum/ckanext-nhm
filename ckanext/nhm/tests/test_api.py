# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


import nose
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY
from ckantest.factories.data import DataConstants
from ckantest.models import TestBase

from ckan.plugins import toolkit


class TestAPI(TestBase):
    plugins = [u'nhm', u'datastore']

    @classmethod
    def setup_class(cls):
        super(TestAPI, cls).setup_class()
        try:
            toolkit.get_action(u'vocabulary_show')({}, {
                u'id': DATASET_TYPE_VOCABULARY
                })
        except toolkit.ObjectNotFound:
            vocab = toolkit.get_action(u'vocabulary_create')(cls.data_factory().context, {
                u'name': DATASET_TYPE_VOCABULARY
                })
            toolkit.get_action(u'tag_create')(cls.data_factory().context, {
                u'name': u'test_tag',
                u'vocabulary_id': vocab[u'id']
                })
        cls.pkg_dict = cls.data_factory().package(dataset_category=u'test_tag')
        cls.res_dict = cls.data_factory().resource(package_id=cls.pkg_dict[u'id'],
                                                   records=DataConstants.records)

    def test_show_package(self):
        params = {
            u'id': self.pkg_dict[u'name']
            }
        response = self.api_request(u'package_show', params=params)

        nose.tools.assert_true(response[u'success'])
        nose.tools.assert_dict_equal(response[u'result'],
                                     self.data_factory().packages[self.pkg_dict[u'name']])

    def test_create_package(self):
        name = u'test_api_create_package'
        params = {
            u'name': name,
            u'dataset_category': u'test_tag',
            u'author': DataConstants.authors_short,
            u'title': name,
            u'notes': u'what exciting notes'
            }
        response = self.api_request(u'package_create', params=params, method=u'post')

        pkg_dict = toolkit.get_action(u'package_show')({}, {
            u'id': name
            })

        nose.tools.assert_true(response[u'success'])
        nose.tools.assert_equal(response[u'result'][u'name'], name)
        nose.tools.assert_equal(pkg_dict[u'name'], name)

    def test_show_resource(self):
        params = {
            u'id': self.res_dict[u'id']
            }
        response = self.api_request(u'resource_show', params=params)
        nose.tools.assert_true(response[u'success'])
        nose.tools.assert_equal(response[u'result'][u'id'], self.res_dict[u'id'])

    def test_create_resource(self):
        params = {
            u'package_id': self.pkg_dict[u'id'],
            u'url': u'http://placekitten.com/500/500',
            u'name': u'test_api_create_resource'
            }
        response = self.api_request(u'resource_create', params=params, method=u'post')
        nose.tools.assert_true(response[u'success'])

    def test_create_group(self):
        params = {
            u'name': u'test-group'
            }
        response = self.api_request(u'group_create', params=params,
                                    method=u'post')
        nose.tools.assert_true(response[u'success'])
