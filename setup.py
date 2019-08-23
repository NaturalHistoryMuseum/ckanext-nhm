#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

# for listing in the requirements as 'ckanext-NAME'
ckan_extensions = ['spatial', 'viewhelpers', 'dcat', 'pdfview', 'contact', 'doi', 'gallery',
                   'userdatasets', 'ldap', 'graph', 'ckanpackager', 'video', 'gbif', 'statistics',
                   'list', 'status', 'twitter', 'sketchfab', 'versioned_datastore',
                   'versioned_tiledmap', 'query_dois', ]

# to avoid repeating this URL near 20 times
nhm_git = 'git+https://github.com/NaturalHistoryMuseum/'

setup(
    name=u'ckanext-nhm',
    version=__version__,
    description=u'A CKAN extension for the Natural History Museum\'s Data Portal.',
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
    install_requires=[
                         'PyYAML==3.10',
                         'amqp==1.4.0',
                         'anyjson==0.3.3',
                         'billiard==3.3.0.13',
                         'celery==3.1.7',
                         'pytz==2013.9',
                         'python-memcached==1.53',
                         'lxml>=3.4.4',
                         'Shapely<1.3',
                         'raven==6.0.0',
                         'elasticsearch-dsl',
                         ] + ['ckanext-' + ext for ext in ckan_extensions],
    dependency_links=[
        'git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial',
        'git+https://github.com/ckan/ckanext-viewhelpers.git#egg=ckanext_viewhelpers',
        'git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext_dcat',
        'git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext_pdfview',
        nhm_git + 'ckanext-contact.git#egg=ckanext-contact',
        nhm_git + 'ckanext-doi.git#egg=ckanext-doi',
        nhm_git + 'ckanext-gallery.git#egg=ckanext-gallery',
        nhm_git + 'ckanext-userdatasets.git#egg=ckanext-userdatasets',
        nhm_git + 'ckanext-ldap.git#egg=ckanext-ldap',
        nhm_git + 'ckanext-graph.git#egg=ckanext-graph',
        nhm_git + 'ckanext-ckanpackager.git#egg=ckanext-ckanpackager',
        nhm_git + 'ckanext-video.git#egg=ckanext_video',
        nhm_git + 'ckanext-gbif.git#egg=ckanext_gbif',
        nhm_git + 'ckanext-statistics.git#egg=ckanext_statistics',
        nhm_git + 'ckanext-list.git#egg=ckanext_list',
        nhm_git + 'ckanext-status.git#egg=ckanext_status',
        nhm_git + 'ckanext-twitter.git#egg=ckanext_twitter',
        nhm_git + 'ckanext-sketchfab.git#egg=ckanext_sketchfab',
        nhm_git + 'ckanext-versioned-datastore.git#egg=ckanext_versioned_datastore',
        nhm_git + 'ckanext-versioned-tiledmap.git#egg=ckanext_versioned_tiledmap',
        nhm_git + 'ckanext-query-dois.git#egg=ckanext_query_dois',
        ],
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
