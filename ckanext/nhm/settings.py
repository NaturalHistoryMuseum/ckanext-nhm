#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK
from collections import OrderedDict

# the order here matters as the default option should always be first in the dict so that it is
# automatically selected in combo boxes that use this list as a source for options
COLLECTION_CONTACTS = OrderedDict([
    (u'Data Portal / Other', u'data@nhm.ac.uk'),
    (u'Algae, Fungi & Plants', u'm.carine@nhm.ac.uk'),
    (u'Economic & Environmental Earth Sciences', u'g.miller@nhm.ac.uk'),
    (u'Fossil Invertebrates & Plants', u'z.hughes@nhm.ac.uk@nhm.ac.uk'),
    (u'Fossil Vertebrates & Anthropology', u'm.richter@nhm.ac.uk'),
    (u'Insects', u'g.broad@nhm.ac.uk'),
    (u'Invertebrates', u'm.lowe@nhm.ac.uk'),
    (u'Library & Archives', u'library@nhm.ac.uk'),
    (u'Mineral & Planetary Sciences', u'm.rumsey@nhm.ac.uk'),
    (u'Vertebrates', u'simon.loader@nhm.ac.uk'),
])
