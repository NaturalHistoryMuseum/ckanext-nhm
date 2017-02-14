#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


import unittest
import itertools
from operator import itemgetter
from ke2mongo.tasks.specimen import SpecimenCSVTask
from ckanext.nhm.controllers.specimen import SpecimenController

# TODO: Temp, need to look at this http://docs.ckan.org/en/1117-start-new-test-suite/testing-coding-standards.html
# But in the meantime I just want some quick tests


class FieldsTest(unittest.TestCase):

    def test_specimen_fields(self):
        """
        Make sure all the fields defined in the CSV task are output in the record view
        @return:
        """

        # Fields we know we do not want to output on record view
        field_blacklist = ['_id', 'institutionCode', 'basisOfRecord', 'dynamicProperties']

        # Get all the columns defined in SpecimenCSVTask
        cols = [c[1] for c in itertools.chain(SpecimenCSVTask.columns, SpecimenCSVTask.dynamic_property_columns) if c[1] not in field_blacklist]

        for group, fields in SpecimenController.field_groups.items():
            for field in fields:
                self.assertIn(field[0], cols)
                cols.remove(field[0])

        self.assertListEqual([], cols)

if __name__ == '__main__':
    unittest.main()

