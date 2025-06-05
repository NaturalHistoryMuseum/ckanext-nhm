#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import logging
from collections import OrderedDict

from ckan.plugins import toolkit

from ckanext.nhm.lib.filter_options import has_image, has_lat_long
from ckanext.nhm.views.default import DefaultView

log = logging.getLogger(__name__)


def modify_field_groups(field_groups):
    """
    Given a FieldGroups object from the vds plugin, force certain field groups to show
    in multisearch results and force certain field groups to be ignored and not shown.

    :param field_groups: a FieldGroups object
    """
    # forces
    field_groups.force('scientificName')
    field_groups.force('identifier')
    field_groups.force('preparationType')
    field_groups.force('preparationContents')
    field_groups.force('preparationProcess')
    field_groups.force('preservation')
    field_groups.force('preparationDate')
    field_groups.force('barcode')
    field_groups.force('occurrenceID')
    field_groups.force('associatedOccurrences')
    field_groups.force('associatedMediaCount')
    field_groups.force('order')
    field_groups.force('identifiedBy')
    field_groups.force('locality')
    field_groups.force('decimalLatitude')
    field_groups.force('decimalLongitude')
    # ignores
    field_groups.ignore('created')
    field_groups.ignore('modified')
    field_groups.ignore('associatedMedia.*')


class SampleView(DefaultView):
    """
    Controller for displaying a sample record.
    """

    resource_id = toolkit.config.get('ckanext.nhm.sample_resource_id')

    field_facets = [
        'project',
        'order',
        'preparationType',
        'preparationContents',
        'preparationProcess',
    ]

    # Additional search filter options
    filter_options = [has_image, has_lat_long]

    field_groups = OrderedDict(
        [
            (
                'Project',
                OrderedDict(
                    [
                        ('project', 'Project'),
                    ]
                ),
            ),
            (
                'Preparation',
                OrderedDict(
                    [
                        ('preparationDate', 'Preparation Date'),
                        ('preparationType', 'Preparation Type'),
                        ('preparationProcess', 'Preparation Process'),
                        ('identifier', 'Preparation Number'),
                        ('preservation', 'Preservation'),
                        ('preparationContents', 'Preparation Contents'),
                        ('occurrenceID', 'Occurrence ID'),
                    ]
                ),
            ),
            (
                'Specimen',
                OrderedDict(
                    [
                        ('associatedOccurrences', 'Voucher specimen'),
                        ('associatedMediaCount', 'Image Count'),
                        ('barcode', 'Barcode'),
                        ('scientificName', 'Scientific Name'),
                        ('order', 'Order'),
                        ('identifiedBy', 'Identified By'),
                        ('locality', 'Locality'),
                        ('decimalLatitude', 'Decimal Latitude'),
                        ('decimalLongitude', 'Decimal Longitude'),
                    ]
                ),
            ),
            (
                'Record',
                OrderedDict(
                    [
                        ('GUID', 'GUID'),
                        ('modified', 'Modified'),
                        ('created', 'Created'),
                    ]
                ),
            ),
        ]
    )

    def render_record(self, c):
        """

        :param c:

        """
        c.field_groups = self.field_groups
        return toolkit.render('record/collection.html')
