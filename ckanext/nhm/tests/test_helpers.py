# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import nose
from ckanext.nhm.lib.helpers import dataset_author_truncate
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
