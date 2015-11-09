from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
from ckan.lib.helpers import link_to
import logging
import json
from ckanext.nhm.lib.helpers import resource_view_get_view
from ckanext.nhm.views import DarwinCoreView


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

    Loads all the data and then defers render function to view objects
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
            record = get_action('record_get')(self.context, {'resource_id': resource_id, 'record_id': record_id})
            c.record_dict = record['data']
            record_field_types = {f['id']: f['type'] for f in record['fields']}

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        field_names = {
            'image': c.resource.get('_image_field', None),
            'title': c.resource.get('_title_field', None),
            'latitude': None,
            'longitude': None
        }
        # Get lat/long fields
        # Loop through all the views - if we have a tiled map view with lat/lon fields
        # We'll use those fields to add the map
        views = p.toolkit.get_action('resource_view_list')(self.context, {'id': resource_id})
        for view in views:
            if view['view_type'] == TILED_MAP_TYPE:
                field_names['latitude'] = view[u'latitude_field']
                field_names['longitude'] = view[u'longitude_field']
                break

        # If this is a DwC dataset, add some default for image and lat/lon fields
        if c.resource['format'].lower() == 'dwc':
            for field_name, dwc_field in [('latitude', 'decimalLatitude'), ('longitude', 'decimalLongitude')]:
                if dwc_field in c.record_dict:
                    field_names[field_name] = dwc_field

        # Assign title based on the title field
        c.record_title = c.record_dict.get(field_names['title'], 'Record %s' % c.record_dict.get('_id'))

        # Sanity check: image field hasn't been set to _id
        if field_names['image'] and field_names['image'] != '_id':

            try:
                image_field_type = record_field_types[field_names['image']]
            except KeyError:
                pass
            else:
                default_copyright = '<small>&copy; The Trustees of the Natural History Museum, London</small>'
                licence_id = c.resource.get('_image_licence') or 'ODC-BY-1.0'
                licence = model.Package.get_license_register()[licence_id]
                default_licence = 'Licence: %s' % link_to(licence.title, licence.url, target='_blank')

                image_field_value = c.record_dict.pop(field_names['image'])

                if image_field_value:

                    if image_field_type == 'json':

                        c.images = []

                        try:
                            images = json.loads(image_field_value)
                        except ValueError:
                            pass
                        else:

                            for image in images:
                                href = image.get('identifier', None)
                                if href:
                                    license = link_to(image.get('license'), image.get('license')) if image.get('license', None) else None
                                    c.images.append({
                                        'title': image.get('title', None) or c.record_title,
                                        'href': href,
                                        'copyright': '%s<br />%s' % (license or default_licence, image.get('rightsHolder', None) or default_copyright),
                                        'record_id': record_id,
                                        'resource_id': resource_id
                                    })
                    else:
                        try:
                            # Pop the image field so it won't be output as part of the record_dict / field_data dict (see self.view())
                            c.images = [{'title': c.record_title, 'href': image.strip(), 'copyright': '%s<br />%s' % (default_licence, default_copyright)} for image in image_field_value.split(';') if image.strip()]
                        except (KeyError, AttributeError):
                            # Skip errors - there are no images
                            pass

        if field_names['latitude'] and field_names['longitude']:
            latitude, longitude = c.record_dict.get(field_names['latitude']), c.record_dict.get(field_names['longitude'])

            if latitude and longitude:
                c.record_map = json.dumps({
                    'type': 'Point',
                    'coordinates': [longitude, latitude]
                })


    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        self._load_data(package_name, resource_id, record_id)

        view_cls = resource_view_get_view(c.resource)

        return view_cls.render_record(c)

    def dwc(self, package_name, resource_id, record_id):
        """
        Explicit DwC view
        @param package_name:
        @param resource_id:
        @param record_id:
        @return:
        """

        self._load_data(package_name, resource_id, record_id)

        # Is this a DwC view of an additional dataset?
        # In which case, provide links back to the original record view
        c.additional_view = True

        view = DarwinCoreView()
        return view.render_record(c)