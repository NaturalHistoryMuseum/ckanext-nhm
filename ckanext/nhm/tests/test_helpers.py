#!/usr/bin/env python
# encoding: utf-8

import unittest

from ckanext.nhm.lib.helpers import dataset_author_truncate


class AuthorTruncateTest(unittest.TestCase):
    '''
    Tests for the dataset_author_truncate helper function.
    '''

    def test_untruncated_author(self):
        '''
        dataset_author_truncate shouldn't truncate when the author is shorter than the max
        '''
        author = u'Dr. Someone'
        self.assertEqual(author, dataset_author_truncate(author))

    def test_untruncated_unicode_author(self):
        '''
        dataset_author_truncate shouldn't truncate when the author is longer than the max
        and contains unicode characters
        '''
        author = u'Dr. Someoné'
        self.assertEqual(author, dataset_author_truncate(author))

    def test_truncated_author(self):
        '''
        dataset_author_truncate should truncate when the author is longer than the max
        '''
        author = u', '.join([u'Dr. Someone']*10)
        try:
            dataset_author_truncate(author)
        except UnicodeEncodeError:
            self.fail("Test unexpectantly threw UnicodeEncodeError when it shouldn't have")

    def test_truncated_unicode_author(self):
        '''
        dataset_author_truncate should truncate when the author is longer than the max
        and contains unicode characters
        '''
        author = u', '.join([u'Dr. Someoné']*10)
        try:
            dataset_author_truncate(author)
        except UnicodeEncodeError:
            self.fail("Test unexpectantly threw UnicodeEncodeError when it shouldn't have")


if __name__ == '__main__':
    unittest.main()
