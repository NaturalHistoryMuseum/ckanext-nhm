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


class SampleView(DefaultView):
    """
    Controller for displaying a sample record.
    """

    resource_id = toolkit.config.get("ckanext.nhm.sample_resource_id")

    field_facets = [
        "project",
        "order",
        "preparationType",
        "preparationContents",
        "preparationProcess",
    ]

    # Additional search filter options
    filter_options = [has_image, has_lat_long]

    field_groups = OrderedDict(
        [
            (
                "Project",
                OrderedDict(
                    [
                        ("project", "Project"),
                    ]
                ),
            ),
            (
                "Preparation",
                OrderedDict(
                    [
                        ("preparationDate", "Preparation Date"),
                        ("preparationType", "Preparation Type"),
                        ("preparationProcess", "Preparation Process"),
                        ("identifier", "Preparation Number"),
                        ("preservation", "Preservation"),
                        ("preparationContents", "Preparation Contents"),
                        ("occurrenceID", "Occurrence ID"),
                    ]
                ),
            ),
            (
                "Specimen",
                OrderedDict(
                    [
                        ("associatedOccurrences", "Voucher specimen"),
                        ("associatedMediaCount", "Image Count"),
                        ("barcode", "Barcode"),
                        ("scientificName", "Scientific Name"),
                        ("order", "Order"),
                        ("identifiedBy", "Identified By"),
                        ("locality", "Locality"),
                        ("decimalLatitude", "Decimal Latitude"),
                        ("decimalLongitude", "Decimal Longitude"),
                    ]
                ),
            ),
            (
                "Record",
                OrderedDict(
                    [
                        ("GUID", "GUID"),
                        ("modified", "Modified"),
                        ("created", "Created"),
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
        return toolkit.render("record/collection.html")
