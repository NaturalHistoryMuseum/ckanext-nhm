from importlib.metadata import version

import pytest

from ckanext.nhm.logic.action import show_extension_versions

PACKAGE_NAME = 'ckanext-nhm'


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
# we have a chained datastore_search action so we need a plugin which provides this
# action otherwise this test won't even startup. We could add versioned_datastore but
# adding datastore is easier as it won't complain about various config items that aren't
# set
@pytest.mark.ckan_config('ckan.plugins', 'datastore nhm')
@pytest.mark.usefixtures('with_plugins')
def test_when_loaded():
    extensions = show_extension_versions({}, {})
    assert PACKAGE_NAME in extensions
    assert extensions[PACKAGE_NAME] == version(PACKAGE_NAME)
