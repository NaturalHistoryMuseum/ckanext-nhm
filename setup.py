from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(
	name='ckanext-nhm',
	version=version,
	description="",
	long_description="""""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Ben Scott',
	author_email='',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.nhm'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
            nhm = ckanext.nhm.plugin:NHMPlugin

	    [paste.paster_command]
            dataset-category=ckanext.nhm.commands.dataset_category:DatasetCategoryCommand
            initdb=ckanext.nhm.commands.initdb:InitDBCommand
            datastore=ckanext.nhm.commands.datastore:DatastoreCommand
	""",
)
