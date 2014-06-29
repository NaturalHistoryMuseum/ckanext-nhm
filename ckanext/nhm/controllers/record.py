from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
import json
from ckanext.nhm.lib.helpers import get_datastore_fields, record_display_name
from collections import OrderedDict

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

TILED_MAP_TYPE = 'tiledmap'  # The view type for the tiledmap

class RecordController(base.BaseController):
    """
    Controller for displaying an individual record
    """

    def _load_data(self, package_name, resource_id, record_id):
        """
        Load the data for dataset, resource and record (into C var)
        @param package_name:
        @param resource_id:
        @param record_id:
        @return:
        """
        self.context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # Try & get the resource
        try:
            c.resource = get_action('resource_show')(self.context, {'id': resource_id})
            c.package = get_action('package_show')(self.context, {'id': package_name})
            # required for nav menu
            c.pkg = self.context['package']
            c.pkg_dict = c.package
            c.record_dict = get_action('record_get')(self.context, {'resource_id': resource_id, 'record_id': record_id})
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)


        c.record_dict['SummaryData'] = c.record_dict['SummaryData'].encode('raw_unicode_escape').decode('utf-8')

        # c.record_dict['SummaryData'] = u'C\xe1ceres'

        image_field = c.resource.get('_image_field', None)
        if image_field:
            try:
                # Pop the image field so it won't be output as part of the record_dict / field_data dict (see self.view())
                images = [image.strip() for image in c.record_dict.pop(image_field).split(';')]
            except (KeyError, AttributeError):
                # Skip errors - there are no images
                pass
            else:
                title = record_display_name(c.resource, c.record_dict)
                c.images = [{'title': title, 'url': image} for image in images]

        # Loop through all the views - if we have a tiled map view with lat/lon fields
        # We'll use those fields to add the map
        views = p.toolkit.get_action('resource_view_list')(self.context, {'id': resource_id})

        for view in views:
            if view['view_type'] == TILED_MAP_TYPE:
                latitude, longitude = c.record_dict.get(view[u'latitude_field']), c.record_dict.get(view[u'longitude_field'])

                if latitude and longitude:
                    c.record_map = json.dumps({
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    })

                break

    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """
        self._load_data(package_name, resource_id, record_id)

        # The record_dict does not have field sin the correct order
        # So load the fields, and create an OrderedDict with field: value
        c.field_data = OrderedDict()
        for field in get_datastore_fields(resource_id):
            if not field['id'].startswith('_'):
                c.field_data[field['id']] = c.record_dict.get(field['id'], None)

        # Image and map should be a block in main record view
        return p.toolkit.render('record/view.html')