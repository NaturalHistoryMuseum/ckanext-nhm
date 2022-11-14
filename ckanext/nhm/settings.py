#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from collections import OrderedDict

# the order here matters as the default option should always be first in the dict so that it is
# automatically selected in combo boxes that use this list as a source for options
COLLECTION_CONTACTS = OrderedDict(
    [
        ('Algae, Fungi & Plants', 'm.carine@nhm.ac.uk'),
        ('Economic & Environmental Earth Sciences', 'g.miller@nhm.ac.uk'),
        ('Fossil Invertebrates & Plants', 'z.hughes@nhm.ac.uk'),
        ('Fossil Vertebrates & Anthropology', 'm.richter@nhm.ac.uk'),
        ('Insects', 'g.broad@nhm.ac.uk'),
        ('Invertebrates', 'm.lowe@nhm.ac.uk'),
        ('Library & Archives', 'library@nhm.ac.uk'),
        ('Mineral & Planetary Sciences', 'm.rumsey@nhm.ac.uk'),
        ('Vertebrates', 'simon.loader@nhm.ac.uk'),
        ('Data Portal / Other', 'data@nhm.ac.uk'),
    ]
)
