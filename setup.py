from setuptools import find_packages, setup

version = u'0.4'

setup(
    name=u'ckanext-nhm',
    version=version,
    description=u'',
    long_description=u'''''',
    classifiers=[],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords=u'',
    author=u'Natural History Museum',
    author_email=u'',
    url=u'',
    license=u'',
    packages=find_packages(exclude=[u'ez_setup', u'examples', u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.nhm'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        ],
    entry_points= \
        u'''
            [ckan.plugins]
                nhm = ckanext.nhm.plugin:NHMPlugin
    
            [paste.paster_command]
                dataset-category=ckanext.nhm.commands.dataset_category:DatasetCategoryCommand
                initdb=ckanext.nhm.commands.initdb:InitDBCommand
                datastore=ckanext.nhm.commands.datastore:DatastoreCommand
                file=ckanext.nhm.commands.file:FileCommand
    
            [ckan.rdf.profiles]
                nhm_dcat=ckanext.nhm.dcat.profiles:NHMDCATProfile
        ''',
    )
