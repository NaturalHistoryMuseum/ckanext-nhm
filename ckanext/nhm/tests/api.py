#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


import unittest
import urllib
import urllib2
import json
from urllib2 import HTTPError

# TODO: Temp, need to look at this http://docs.ckan.org/en/1117-start-new-test-suite/testing-coding-standards.html
# But in the meantime I just want some quick tests

class APITest(unittest.TestCase):

    def _request(self, action, params):

                # Use the json module to dump the dictionary to a string for posting.
        data_string = urllib.quote(json.dumps(params))

        # We'll use the package_create function to create a new dataset.
        request = urllib2.Request('http://10.11.12.13:5000/api/3/action/%s' % action)


        # request = urllib2.Request('http://10.11.12.13:5000/api/action/package_create')

        request.add_header('Authorization', '41e326d1-90b4-4381-b3a2-8757ac2b9e3f')

        # Make the HTTP request.
        response = urllib2.urlopen(request, data_string)
        return json.load(response)


    def test_create_resource(self):

        name = 'test17'

        x = json.dumps({"one": "two", "three": "four"})

        try:
            response = self._request('package_show', {'id': name})
            resource_id = response['result']['resources'][0]['id']
        except HTTPError:  # Doesn't exist
            response = self._request('package_create', {'name': name})

            # Create the datastore itself
            datastore_params = {
                'records': [{"dob": "2005", "some_stuff": [x]}, {"dob": "2005", "some_stuff": ["three", "four"]}],
                'resource': {
                    'name': 'test',
                    'description': 'test',
                    'package_id': response['result']['id'],
                }
            }

            response = self._request('datastore_create', datastore_params)
            resource_id = response['result']['resource_id']

        # print resource_id


if __name__ == '__main__':
    unittest.main()