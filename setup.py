#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()


def nhm(repo):
    return u'git+https://github.com/NaturalHistoryMuseum/{0}#egg={0}'.format(repo)


dependencies = {
#    u'ckanext-spatial': u'git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial',
#    u'ckanext-viewhelpers': u'git+https://github.com/ckan/ckanext-viewhelpers.git#egg=ckanext-viewhelpers',
#    u'ckanext-dcat': u'git+https://github.com/ckan/ckanext-dcat.git@v1.0.0#egg=ckanext-dcat',
#    u'ckanext-pdfview': u'git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext-pdfview',
}
nhm_extensions = [
#    u'ckanext-ckanpackager',
#    u'ckanext-contact',
#    u'ckanext-doi',
#    u'ckanext-gallery',
#    u'ckanext-gbif',
#    u'ckanext-graph',
#    u'ckanext-iiif',
#    u'ckanext-ldap',
#    u'ckanext-list',
#    u'ckanext-query-dois',
#    u'ckanext-sketchfab',
#    u'ckanext-statistics',
#    u'ckanext-status',
#    u'ckanext-twitter',
#    u'ckanext-userdatasets',
#    u'ckanext-versioned-datastore',
#    u'ckanext-versioned-tiledmap',
#    u'ckanext-video',
]
dependencies.update({extension: nhm(extension) for extension in nhm_extensions})

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
        u'PyYAML==5.3.1',
        u'amqp==1.4.9',
        u'anyjson==0.3.3',
        u'billiard==3.3.0.13',
        u'celery==3.1.7',
        u'pytz>=2016.7',
        u'python-memcached==1.53',
        u'lxml>=3.4.4',
        u'Shapely<1.3',
        u'raven==6.0.0',
        u'elasticsearch-dsl>=6.0.0,<7.0.0',
        ] + [u'{0} @ {1}'.format(k, v) for k, v in dependencies.items()],
    dependency_links=dependencies.values(),
    entry_points= \
        u'''
        [ckan.plugins]
            nhm=ckanext.nhm.plugin:NHMPlugin

        [paste.paster_command]
            file=ckanext.nhm.commands.file:FileCommand

        [ckan.rdf.profiles]
            nhm_dcat=ckanext.nhm.dcat.profiles:NHMDCATProfile
        ''',
    )
