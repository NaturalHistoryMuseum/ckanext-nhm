#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

from collections import OrderedDict
from setuptools import find_packages, setup

__version__ = u'2.0.0'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()


def github(name, tag, org=u'NaturalHistoryMuseum'):
    # ssh://git@
    #              git+ssh://git@github.com/someorgname/pkg-repo-name@v1.1#egg=some-pkg'
    return name, u'git+https://github.com/{org}/{name}@{tag}#egg={name}'.format(name=name, org=org,
                                                                                tag=tag)


ckan_extensions = OrderedDict([
    # each of these hashes points to the last commit where python2 was supported
    github(u'ckanext-ckanpackager', u'319bd63158757a9287336034122cae66c2991a41'),
    github(u'ckanext-contact', u'6d90f5aa05116bc465a808440ad51d6b3d441067'),
    github(u'ckanext-dcat', u'v1.0.0', org=u'ckan'),
    github(u'ckanext-doi', u'ec452888a5257acea78729bfb64f7c1b8d53eabd'),
    github(u'ckanext-gbif', u'3ca6085134fa668345c747e1f7ce240522718b0c'),
    github(u'ckanext-graph', u'1884ee632fc305c5ade70c89b4485efb787efe4f'),
    github(u'ckanext-ldap', u'900985b2d357fe090c63bf8609f310c8dec05342'),
    github(u'ckanext-query-dois', u'7d701ff1a93810ce3281e1b75eaf4c59951fb574'),
    github(u'ckanext-statistics', u'30dc16aa6646de35ef259f4a98e2837264c6de14'),
    github(u'ckanext-versioned-datastore', u'd88e167a838e95af2448b60c7df67f2e2fe86eed'),
])

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
        # extensions we need to be installed too
    ] + [u'{0} @ {1}'.format(*extension) for extension in ckan_extensions.items()],
    dependency_links=ckan_extensions.values(),
    entry_points=u'''
        [ckan.plugins]
            nhm=ckanext.nhm.plugin:NHMPlugin

        [ckan.rdf.profiles]
            nhm_dcat=ckanext.nhm.dcat.profiles:NHMDCATProfile
        ''',
)
