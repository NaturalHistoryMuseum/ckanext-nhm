import json
import logging

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, c
from ckan.lib.helpers import link_to, url_for
from ckanext.nhm.lib.helpers import resource_view_get_view
from ckanext.nhm.lib.jinja_extensions import TaxonomyFormatExtension
from ckanext.nhm.views import DarwinCoreView

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


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
            record = get_action('record_show')(self.context, {'resource_id': resource_id,
                                                              'record_id': record_id})
            c.record_dict = record['data']

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        field_names = {
            'image': c.resource.get('_image_field', None),
            'title': c.resource.get('_title_field', None),
            'latitude': c.resource.get('_latitude_field', None),
            'longitude': c.resource.get('_longitude_field', None),
        }

        # if this is a DwC dataset, add some default for image and lat/lon fields
        if c.resource['format'].lower() == 'dwc':
            for field_name, dwc_field in [('latitude', 'decimalLatitude'),
                                          ('longitude', 'decimalLongitude')]:
                if dwc_field in c.record_dict:
                    field_names[field_name] = dwc_field

        # assign title based on the title field
        c.record_title = c.record_dict.get(field_names['title'],
                                           'Record {}'.format(c.record_dict.get('_id')))

        # sanity check: image field hasn't been set to _id
        if field_names['image'] and field_names['image'] != '_id':
            default_copyright = '<small>&copy; The Trustees of the Natural History Museum, London</small>'
            licence_id = c.resource.get('_image_licence') or 'cc-by'
            short_licence_id = licence_id[:5].lower()
            # try and overwrite default licence with more specific one
            for l_id in [licence_id, short_licence_id]:
                try:
                    licence = model.Package.get_license_register()[l_id]
                    break
                except KeyError:
                    continue

            default_licence = 'Licence: %s' % link_to(licence.title, licence.url, target='_blank')

            # pop the image field so it isn't output as part of the record_dict/field_data dict
            # (see self.view())
            image_field_value = c.record_dict.pop(field_names['image'], None)

            if image_field_value:
                # init the images list on the context var
                c.images = []
                if isinstance(image_field_value, list):
                    for image in image_field_value:
                        href = image.get('identifier', None)
                        if href:
                            license_link = link_to(image.get('license'), image.get('license')) if image.get('license', None) else None
                            c.images.append({
                                'title': image.get('title', None) or c.record_title,
                                'href': href,
                                'copyright': '%s<br />%s' % (license_link or default_licence, image.get('rightsHolder', None) or default_copyright),
                                'record_id': record_id,
                                'resource_id': resource_id,
                                'link': url_for(
                                    controller='ckanext.nhm.controllers.record:RecordController',
                                    action='view',
                                    package_name=package_name,
                                    resource_id=resource_id,
                                    record_id=record_id
                                ),
                            })
                else:
                    # it's a string field value, use the delimiter to split up the field value (if
                    # there is one!)
                    delimiter = c.resource.get('_image_delimiter', None)
                    if delimiter:
                        images = image_field_value.split(delimiter)
                    else:
                        images = [image_field_value]
                    # loop through the images, adding dicts with their details to the context
                    for image in images:
                        if image.strip():
                            c.images.append({
                                'title': c.record_title,
                                'href': image.strip(),
                                'copyright': '%s<br />%s' % (default_licence, default_copyright)
                            })

        if field_names['latitude'] and field_names['longitude']:
            latitude = c.record_dict.get(field_names['latitude'])
            longitude = c.record_dict.get(field_names['longitude'])

            if latitude and longitude:
                # create a piece of GeoJSON to point at the specific record location on a map
                c.record_map = json.dumps({
                    'type': 'Point',
                    'coordinates': [float(longitude), float(latitude)]
                })

    def view(self, package_name, resource_id, record_id):
        """
        View an individual record
        @param package_name:
        @param resource_id:
        @param record_id:
        @return:
        """
        self._load_data(package_name, resource_id, record_id)

        view_cls = resource_view_get_view(c.resource)

        # Load the taxonomy formatter
        c.pylons.app_globals.jinja_env.add_extension(
            TaxonomyFormatExtension)

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
