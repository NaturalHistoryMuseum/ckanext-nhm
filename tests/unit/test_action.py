import pytest

from importlib.metadata import version

from ckanext.nhm.logic.action import show_extension_versions


PACKAGE_NAME = 'ckanext-nhm'


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
class TestShowExtensionVersions:
    @pytest.mark.ckan_config('ckan.plugins', 'nhm')
    @pytest.mark.usefixtures('with_plugins')
    def test_when_loaded(self):
        extensions = show_extension_versions({}, {})
        assert PACKAGE_NAME in extensions
        assert extensions[PACKAGE_NAME] == version(PACKAGE_NAME)

    def test_when_not_loaded(self):
        extensions = show_extension_versions({}, {})
        assert PACKAGE_NAME not in extensions
