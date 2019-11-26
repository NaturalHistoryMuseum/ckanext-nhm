#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

nhmgit = 'git+https://github.com/NaturalHistoryMuseum/'

dependencies = {'ckanext-spatial': 'git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial',
'ckanext-viewhelpers': 'git+https://github.com/ckan/ckanext-viewhelpers.git#egg=ckanext_viewhelpers',
'ckanext-dcat': 'git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext_dcat',
'ckanext-pdfview': 'git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext_pdfview',
'ckanext-contact': nhmgit + 'ckanext-contact.git#egg=ckanext-contact',
'ckanext-doi': nhmgit + 'ckanext-doi.git#egg=ckanext-doi',
'ckanext-gallery': nhmgit + 'ckanext-gallery.git#egg=ckanext-gallery',
'ckanext-userdatasets': nhmgit + 'ckanext-userdatasets.git#egg=ckanext-userdatasets',
'ckanext-ldap': nhmgit + 'ckanext-ldap.git#egg=ckanext-ldap',
'ckanext-graph': nhmgit + 'ckanext-graph.git#egg=ckanext-graph',
'ckanext-ckanpackager': nhmgit + 'ckanext-ckanpackager.git#egg=ckanext-ckanpackager',
'ckanext-video': nhmgit + 'ckanext-video.git#egg=ckanext_video',
'ckanext-gbif': nhmgit + 'ckanext-gbif.git#egg=ckanext_gbif',
'ckanext-statistics': nhmgit + 'ckanext-statistics.git#egg=ckanext_statistics',
'ckanext-list': nhmgit + 'ckanext-list.git#egg=ckanext_list',
'ckanext-status': nhmgit + 'ckanext-status.git#egg=ckanext_status',
'ckanext-twitter': nhmgit + 'ckanext-twitter.git#egg=ckanext_twitter',
'ckanext-sketchfab': nhmgit + 'ckanext-sketchfab.git#egg=ckanext_sketchfab',
'ckanext-versioned-datastore': nhmgit + 'ckanext-versioned-datastore.git#egg=ckanext_versioned_datastore',
'ckanext-versioned-tiledmap': nhmgit + 'ckanext-versioned-tiledmap.git#egg=ckanext_versioned_tiledmap',
'ckanext-query-dois': nhmgit + 'ckanext-query-dois.git#egg=ckanext_query_dois',}

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
        'amqp==1.4.9',
        'anyjson==0.3.3',
        'billiard==3.3.0.13',
        'celery==3.1.7',
        'pytz>=2016.7',
        'python-memcached==1.53',
        'lxml>=3.4.4',
        'Shapely<1.3',
        'raven==6.0.0',
        'elasticsearch-dsl==6.2.1',
        ] + [u'{0} @ {1}'.format(k, v) for k, v in dependencies.items()],
    dependency_links=dependencies.values(),
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
