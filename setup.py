#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-nhm',
    version=__version__,
    description=u'A CKAN extension for the Natural History Museum's Data Portal.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data nhm',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-nhm',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.nhm'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        u'''
        [ckan.plugins]
            nhm=ckanext.nhm.plugin:NHMPlugin

        [paste.paster_command]
            dataset-category=ckanext.nhm.commands.dataset_category:DatasetCategoryCommand
            initdb=ckanext.nhm.commands.initdb:InitDBCommand
            datastore=ckanext.nhm.commands.datastore:DatastoreCommand
            file=ckanext.nhm.commands.file:FileCommand

        [ckan.rdf.profiles]
            nhm_dcat=ckanext.nhm.dcat.profiles:NHMDCATProfile
        ''',
    )
