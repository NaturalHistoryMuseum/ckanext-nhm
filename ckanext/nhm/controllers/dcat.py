import json

from ckan.plugins import toolkit

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController
from ckan.controllers.package import PackageController
from ckan.controllers.home import HomeController

from ckanext.dcat.utils import CONTENT_TYPES, parse_accept_header

from ckanext.dcat.controllers import check_access_header


class DCATController(BaseController):

    def read_record(self, _format=None):

        if not _format:
            _format = check_access_header()

        if not _format:
            return HomeController().index()

        data_dict = {
            'page': toolkit.request.params.get('page'),
            'modified_since': toolkit.request.params.get('modified_since'),
            'format': _format,
        }

        return 'HEY'

        # toolkit.response.headers.update(
        #     {'Content-type': CONTENT_TYPES[_format]})
        # try:
        #     return toolkit.get_action('dcat_record_show')({}, data_dict)
        # except toolkit.ValidationError, e:
        #     toolkit.abort(409, str(e))






