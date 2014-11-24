from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
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
            c.record_dict = get_action('record_get')(self.context, {'resource_id': resource_id, 'record_id': record_id})

        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % package_name)

        image_field = c.resource.get('_image_field', None)
        title_field = c.resource.get('_title_field', None)

        c.record_title = c.record_dict.get(title_field, 'Record %s' % c.record_dict.get('_id'))

        # Sanity check: image field hasn't been set to _id

        from ckan.lib.helpers import url_for, link_to

        if image_field and image_field != '_id':

            description = None
            licence_id = c.resource.get('_image_licence', None)

            if licence_id:
                licence = model.Package.get_license_register()[licence_id]
                description = 'Licence: %s' % link_to(licence.title, licence.url, target='_blank')

            try:
                # Pop the image field so it won't be output as part of the record_dict / field_data dict (see self.view())
                c.images = [{'modal_title': c.record_title, 'url': image.strip(), 'description': description} for image in c.record_dict.pop(image_field).split(';') if image.strip()]
            except (KeyError, AttributeError):
                # Skip errors - there are no images
                pass

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