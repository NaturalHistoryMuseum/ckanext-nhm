
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK


import unittest
import itertools
from operator import itemgetter
from ke2mongo.tasks.specimen import SpecimenCSVTask
from ckanext.nhm.controllers.specimen import SpecimenController



class FieldsTest(unittest.TestCase):
    ''' '''

    def test_specimen_fields(self):
        '''Make sure all the fields defined in the CSV task are output in the record view'''

        # Fields we know we do not want to output on record view
        field_blacklist = [u'_id', u'institutionCode', u'basisOfRecord', u'dynamicProperties']

        # Get all the columns defined in SpecimenCSVTask
        cols = [c[1] for c in itertools.chain(SpecimenCSVTask.columns, SpecimenCSVTask.dynamic_property_columns) if c[1] not in field_blacklist]

        for group, fields in SpecimenController.field_groups.items():
            for field in fields:
                self.assertIn(field[0], cols)
                cols.remove(field[0])

        self.assertListEqual([], cols)

if __name__ == u'__main__':
    unittest.main()


