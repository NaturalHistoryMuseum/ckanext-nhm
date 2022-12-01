#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import setuptools

if __name__ == '__main__':
    setuptools.setup(
        dependency_links=[
            'https://github.com/ckan/ckanext-dcat@v1.3.0#egg=ckanext-dcat'
        ]
    )
