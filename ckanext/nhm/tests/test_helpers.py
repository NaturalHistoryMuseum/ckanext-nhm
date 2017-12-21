#!/usr/bin/env python
# encoding: utf-8

import unittest

from datetime import datetime, timedelta

from ckanext.nhm.lib.helpers import dataset_author_truncate,\
    get_last_resource_update_for_package


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


class ResourceLatestModificationDateTest(unittest.TestCase):
    '''
    Tests for the get_last_resource_update_for_package helper function.
    '''

    def setUp(self):
        self.date_format = '%d/%m/%y %H:%M:%S'

    @staticmethod
    def package(resources=None):
        return {'resources': resources if resources else []}

    @staticmethod
    def resource(name, last_modified=None, revision_timestamp=None, created=None):
        return {
            'name': name,
            'last_modified': last_modified,
            'revision_timestamp': revision_timestamp,
            'Created': created
        }

    def test_package_with_no_resources(self):
        '''
        If the package has no resources, unknown should be returned
        '''
        package = self.package()
        latest = get_last_resource_update_for_package(package, self.date_format)
        self.assertEqual('unknown', latest)

    def test_package_with_one_resources(self):
        '''
        If the package has one resource, it's latest modification datetime
        should be returned
        '''
        name = 'r1'
        time = datetime.now()
        package = self.package([self.resource(name, last_modified=time)])
        latest = get_last_resource_update_for_package(package, self.date_format)
        self.assertTrue(latest.startswith(time.strftime(self.date_format)))
        self.assertTrue(name in latest)

    def test_package_with_multiple_resources(self):
        '''
        If the package has more than one resource, then the newest update
        datetime from those resources should be returned
        '''
        name = 'r1'
        time = datetime.now()
        package = self.package([
            self.resource('r1', last_modified=time - timedelta(hours=1)),
            self.resource(name, revision_timestamp=time),
            self.resource('r3', created=time - timedelta(hours=5))
        ])
        latest = get_last_resource_update_for_package(package, self.date_format)
        self.assertTrue(latest.startswith(time.strftime(self.date_format)))
        self.assertTrue(name in latest)

    def test_resource_with_no_dates(self):
        '''
        If the package has a resource, but the resource has no update datetimes
        then 'unknown' should be returned
        '''
        package = self.package([self.resource('r1')])
        latest = get_last_resource_update_for_package(package)
        self.assertEqual('unknown', latest)

    def test_resource_with_dates(self):
        '''
        If the package has a resource and the resource has update datetimes,
        then the latest one should be returned
        '''
        name = 'r1'
        time = datetime.now()
        package = self.package([
            self.resource(name, last_modified=time - timedelta(hours=1),
                          revision_timestamp=time,
                          created=time - timedelta(hours=5))])
        latest = get_last_resource_update_for_package(package, self.date_format)
        self.assertTrue(latest.startswith(time.strftime(self.date_format)))
        self.assertTrue(name in latest)


if __name__ == '__main__':
    unittest.main()
