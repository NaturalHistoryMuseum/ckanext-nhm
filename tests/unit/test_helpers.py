# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from unittest.mock import MagicMock, patch

import pytest
from ckan.plugins import toolkit

from ckanext.nhm.lib.helpers import (
    dataset_author_truncate,
    get_object_url,
    get_specimen_jsonld,
)


class TestAuthorTruncate(object):
    """
    Tests for the dataset_author_truncate helper function.
    """

    def test_untruncated_author(self):
        """
        dataset_author_truncate shouldn't truncate when the author is shorter than the
        max.
        """
        author = 'Dr. Someone'
        assert author == dataset_author_truncate(author)

    def test_untruncated_unicode_author(self):
        """
        dataset_author_truncate shouldn't truncate when the author is shorter than the
        max and contains unicode characters.
        """
        author = 'Dr. Someoné'
        assert author, dataset_author_truncate(author)

    def test_truncated_author(self):
        """
        dataset_author_truncate should truncate when the author is longer than the max.
        """
        author = ', '.join(['Dr. Someone'] * 10)

        truncated = str(dataset_author_truncate(author))
        assert truncated.startswith(
            'Dr. Someone; Dr. Someone; Dr. Someone; Dr. Someone'
        )
        assert truncated.endswith('et al.</abbr>')

    def test_truncated_unicode_author(self):
        """
        dataset_author_truncate should truncate when the author is longer than the max
        and contains unicode characters.
        """
        author = ', '.join(['Dr. Someoné'] * 10)
        truncated = str(dataset_author_truncate(author))
        assert truncated.startswith(
            'Dr. Someoné; Dr. Someoné; Dr. Someoné; Dr. Someoné'
        )
        assert truncated.endswith('et al.</abbr>')


class TestGetObjectURL(object):
    """
    Tests for the get_object_url helper function.
    """

    def test_get_object_url_default(self):
        mock_rounded_version = 10
        mock_datastore_get_rounded_version = MagicMock(
            return_value=mock_rounded_version
        )
        mock_get_action = MagicMock(return_value=mock_datastore_get_rounded_version)
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url('a resource', 'a guid')
            mock_get_action.assert_called_once_with('datastore_get_rounded_version')
            mock_datastore_get_rounded_version.assert_called_once_with(
                {},
                {
                    'resource_id': 'a resource',
                    'version': None,
                },
            )
            mock_url_for.assert_called_once_with(
                'object.view',
                uuid='a guid',
                qualified=True,
                version=mock_rounded_version,
            )

    def test_get_object_url_passed_version(self):
        mock_rounded_version = 10
        mock_datastore_get_rounded_version = MagicMock(
            return_value=mock_rounded_version
        )
        mock_get_action = MagicMock(return_value=mock_datastore_get_rounded_version)
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url('a resource', 'a guid', version=15)
            mock_get_action.assert_called_once_with('datastore_get_rounded_version')
            mock_datastore_get_rounded_version.assert_called_once_with(
                {},
                {
                    'resource_id': 'a resource',
                    'version': 15,
                },
            )
            mock_url_for.assert_called_once_with(
                'object.view',
                uuid='a guid',
                qualified=True,
                version=mock_rounded_version,
            )

    def test_get_object_url_no_version(self):
        mock_get_action = MagicMock()
        mock_url_for = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action, url_for=mock_url_for)
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            get_object_url('a resource', 'a guid', version=15, include_version=False)
            mock_get_action.assert_not_called()
            mock_url_for.assert_called_once_with(
                'object.view', uuid='a guid', qualified=True, version=None
            )


class TestGetSpecimenJSONLD(object):
    """
    Tests for the get_specimen_jsonld helper function.
    """

    def test_error(self):
        real_validation_error_class = toolkit.ValidationError
        mock_get_action = MagicMock(side_effect=real_validation_error_class('test'))
        mock_toolkit = MagicMock(
            get_action=mock_get_action, ValidationError=real_validation_error_class
        )
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            assert get_specimen_jsonld(MagicMock()) == ''

    def test_normal(self):
        mock_get_action = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action)
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            uuid = 'beans'
            get_specimen_jsonld(uuid)
            mock_get_action.assert_called_once_with('object_rdf')
            mock_get_action('object_rdf').assert_called_once_with(
                {}, {'uuid': uuid, 'format': 'json-ld', 'version': None}
            )

    def test_normal_with_version(self):
        mock_get_action = MagicMock()
        mock_toolkit = MagicMock(get_action=mock_get_action)
        with patch('ckanext.nhm.lib.helpers.toolkit', mock_toolkit):
            uuid = 'beans'
            version = 327947382
            get_specimen_jsonld(uuid, version)
            mock_get_action.assert_called_once_with('object_rdf')
            mock_get_action('object_rdf').assert_called_once_with(
                {}, {'uuid': uuid, 'format': 'json-ld', 'version': 327947382}
            )
