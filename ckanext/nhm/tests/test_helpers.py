# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import nose
from ckan.plugins import toolkit
from mock import MagicMock, patch
from ckanext.nhm.lib.helpers import dataset_author_truncate, get_object_url, get_specimen_jsonld
from ckantest.models import TestBase


class TestAuthorTruncate(TestBase):
    '''Tests for the dataset_author_truncate helper function.'''
    plugins = [u'nhm']

    def test_untruncated_author(self):
        '''dataset_author_truncate shouldn't truncate when the author is shorter
        than the max'''
        author = u'Dr. Someone'
        nose.tools.assert_equal(author, dataset_author_truncate(author))

    def test_untruncated_unicode_author(self):
        '''dataset_author_truncate shouldn't truncate when the author is shorter than
        the max and contains unicode characters'''
        author = u'Dr. Someoné'
        nose.tools.assert_equal(author, dataset_author_truncate(author))

    def test_truncated_author(self):
        '''dataset_author_truncate should truncate when the author is longer
        than the max'''
        author = u', '.join([u'Dr. Someone'] * 10)
        dataset_author_truncate(author)

    def test_truncated_unicode_author(self):
        '''dataset_author_truncate should truncate when the author is longer than the max
        and contains unicode characters'''
        author = u', '.join([u'Dr. Someoné'] * 10)
        dataset_author_truncate(author)


class TestGetObjectURL(TestBase):
    '''Tests for the get_object_url helper function.'''
    plugins = [u'nhm']

    def test_get_object_url_default(self):
        mock_rounded_version = 10
        mock_datastore_get_rounded_version = MagicMock(return_value=mock_rounded_version)
        mock_get_action = MagicMock(return_value=mock_datastore_get_rounded_version)
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url(u'a resource', u'a guid')
            mock_get_action.assert_called_once_with(u'datastore_get_rounded_version')
            mock_datastore_get_rounded_version.assert_called_once_with({}, {
                u'resource_id': u'a resource',
                u'version': None,
            })
            mock_url_for.assert_called_once_with(u'object.view', uuid=u'a guid', qualified=True,
                                                 version=mock_rounded_version)

    def test_get_object_url_passed_version(self):
        mock_rounded_version = 10
        mock_datastore_get_rounded_version = MagicMock(return_value=mock_rounded_version)
        mock_get_action = MagicMock(return_value=mock_datastore_get_rounded_version)
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url(u'a resource', u'a guid', version=15)
            mock_get_action.assert_called_once_with(u'datastore_get_rounded_version')
            mock_datastore_get_rounded_version.assert_called_once_with({}, {
                u'resource_id': u'a resource',
                u'version': 15,
            })
            mock_url_for.assert_called_once_with(u'object.view', uuid=u'a guid', qualified=True,
                                                 version=mock_rounded_version)

    def test_get_object_url_no_version(self):
        mock_get_action = MagicMock()
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url(u'a resource', u'a guid', version=15, include_version=False)
            mock_get_action.assert_not_called()
            mock_url_for.assert_called_once_with(u'object.view', uuid=u'a guid', qualified=True,
                                                 version=None)


class TestGetSpecimenJSONLD(TestBase):
    '''Tests for the get_specimen_jsonld helper function.'''
    plugins = [u'nhm']

    def test_error(self):
        mock_get_action = MagicMock(side_effect=toolkit.ValidationError(u'test'))
        mock_toolkit = MagicMock(get_action=mock_get_action)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            nose.tools.assert_raises(toolkit.ValidationError, get_specimen_jsonld, MagicMock())

    def test_normal(self):
        mock_get_action = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            uuid = u'beans'
            get_specimen_jsonld(uuid)
            mock_get_action.assert_called_once_with(u'object_rdf')
            mock_get_action(u'object_rdf').assert_called_once_with({}, {
                u'uuid': uuid,
                u'format': u'json-ld',
                u'version': None
            })

    def test_normal_with_version(self):
        mock_get_action = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action)
        with patch(u'ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            uuid = u'beans'
            version = 327947382
            get_specimen_jsonld(uuid, version)
            mock_get_action.assert_called_once_with(u'object_rdf')
            mock_get_action(u'object_rdf').assert_called_once_with({}, {
                u'uuid': uuid,
                u'format': u'json-ld',
                u'version': 327947382
            })
