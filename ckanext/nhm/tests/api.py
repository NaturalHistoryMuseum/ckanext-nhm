
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


import unittest
import urllib
import urllib2
import json
from urllib2 import HTTPError


class APITest(unittest.TestCase):
    ''' '''

    def _request(self, action, params):
        '''

        :param action: 
        :param params: 

        '''

                # Use the json module to dump the dictionary to a string for posting.
        data_string = urllib.quote(json.dumps(params))

        # We'll use the package_create function to create a new dataset.
        request = urllib2.Request(u'http://10.11.12.13:5000/api/3/action/%s' % action)


        # request = urllib2.Request('http://10.11.12.13:5000/api/action/package_create')

        request.add_header(u'Authorization', u'41e326d1-90b4-4381-b3a2-8757ac2b9e3f')

        # Make the HTTP request.
        response = urllib2.urlopen(request, data_string)
        return json.load(response)


    def test_create_resource(self):
        ''' '''

        name = u'test17'

        x = json.dumps({u'one': u'two', u'three': u'four'})

        try:
            response = self._request(u'package_show', {u'id': name})
            resource_id = response[u'result'][u'resources'][0][u'id']
        except HTTPError:  # Doesn't exist
            response = self._request(u'package_create', {u'name': name})

            # Create the datastore itself
            datastore_params = {
                u'records': [{u'dob': u'2005', u'some_stuff': [x]}, {u'dob': u'2005', u'some_stuff': [u'three', u'four']}],
                u'resource': {
                    u'name': u'test',
                    u'description': u'test',
                    u'package_id': response[u'result'][u'id'],
                }
            }

            response = self._request(u'datastore_create', datastore_params)
            resource_id = response[u'result'][u'resource_id']

        # print resource_id


if __name__ == u'__main__':
    unittest.main()

