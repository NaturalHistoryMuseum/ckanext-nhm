# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from . import about, legal, statistics, record

blueprints = [about.blueprint, statistics.blueprint, legal.blueprint, record.blueprint]
