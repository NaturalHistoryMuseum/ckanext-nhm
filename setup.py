#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict
from setuptools import find_packages, setup

__version__ = '3.0.25'

with open('README.md', 'r') as f:
    __long_description__ = f.read()


def github(name, tag, org='NaturalHistoryMuseum'):
    return name, f'git+https://github.com/{org}/{name}@{tag}#egg={name}'


ckan_extensions = OrderedDict([
    github('ckanext-dcat', '6b7ec505f303fb18e0eebcebf67130d36b3dca82', org='ckan'),
    github('ckanext-ckanpackager', 'v2.0.0'),
    github('ckanext-contact', 'v2.0.0'),
    github('ckanext-doi', 'v3.0.4'),
    github('ckanext-gallery', 'v2.0.1'),
    github('ckanext-gbif', 'v2.0.0'),
    github('ckanext-graph', 'v2.0.0'),
    github('ckanext-ldap', 'v3.0.1'),
    github('ckanext-query-dois', 'v2.0.4'),
    github('ckanext-statistics', 'v2.0.3'),
    github('ckanext-versioned-datastore', 'v3.1.3'),
])

setup(
    name='ckanext-nhm',
    version=__version__,
    description='A CKAN extension for the Natural History Museum\'s Data Portal.',
    long_description=__long_description__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='CKAN data nhm',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    url='https://github.com/NaturalHistoryMuseum/ckanext-nhm',
    license='GNU GPLv3',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.nhm'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'lxml>=3.4.4',
        'elasticsearch-dsl>=6.0.0,<7.0.0',
        'cachetools>=4.2.4',
        # extensions we need to be installed too
    ] + [f'{name} @ {repo}' for (name, repo) in ckan_extensions.items()],
    dependency_links=list(ckan_extensions.values()),
    entry_points='''
        [ckan.plugins]
            nhm=ckanext.nhm.plugin:NHMPlugin

        [ckan.rdf.profiles]
            nhm_dcat=ckanext.nhm.dcat.profiles:NHMDCATProfile
        ''',
)
