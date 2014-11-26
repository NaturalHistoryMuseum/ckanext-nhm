
import logging
import json
import urllib
import re
import os

from beaker.cache import cache_region
from sqlalchemy import func
from pylons import config
from collections import OrderedDict

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.common import c, _, request
from ckan.lib.helpers import url_for, link_to, snippet, _follow_objects, get_allowed_view_types as ckan_get_allowed_view_types

from ckanext.nhm.lib.form import list_to_form_options
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY, UPDATE_FREQUENCIES
from ckanext.nhm.views import *
from ckanext.nhm.lib.resource import (
    resource_get_ordered_fields,
    resource_filter_options,
    parse_request_filters,
    FIELD_DISPLAY_FILTER,
    resource_filter_get_cookie,
    resource_filter_set_cookie,
    resource_filter_delete_cookie
)

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

get_action = logic.get_action
_check_access = logic.check_access

# Make enumerate available to templates
enumerate = enumerate

re_dwc_field_label = re.compile('([A-Z]+)')

def get_site_statistics():
    stats = dict()
    stats['dataset_count'] = logic.get_action('package_search')({}, {"rows": 1})['count']
    # Get a count of all distinct user IDs
    stats['contributor_count'] = get_contributor_count()
    datastore_stats = get_datastore_stats()
    stats['record_count'] = datastore_stats['total']
    return stats


def get_datastore_stats():

    context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}

    stats = {
        'resources': [],
        'total': 0,
        'date': None,
    }

    resource_counts = model.Session.execute(
        """
        SELECT r.id, r.name, d.count, d.date, p.id as pkg_id, p.title as pkg_title, p.name as pkg_name
        FROM resource r
        INNER JOIN datastore_stats d ON r.id = d.resource_id
        INNER JOIN resource_group rg ON r.resource_group_id = rg.id
        INNER JOIN package p ON rg.package_id = p.id
        WHERE r.state='active' AND p.state='active' AND date = (SELECT date FROM datastore_stats ORDER BY date DESC LIMIT 1)
        ORDER BY count DESC
        """
    );

    for resource in resource_counts:
        try:
            _check_access('resource_show', context, dict(resource))
        except NotAuthorized:
            pass
        else:
            stats['resources'].append(resource)
            stats['total'] += int(resource['count'])
            stats['date'] = resource['date']

    return stats


def get_contributor_count():
    return model.Session.execute("SELECT COUNT(DISTINCT creator_user_id) from package WHERE state='active'").scalar()


def _get_action(action, params):
    """
    Call basic get_action from template
    @param action:
    @param params:
    @return:
    """
    context = {'ignore_auth': True, 'for_view': True}

    try:
        return get_action(action)(context, params)
    except (NotFound, NotAuthorized):
        pass

    return None


def get_package(package_id):
    return _get_action('package_show', {'id': package_id})


def get_resource(resource_id):
    return _get_action('resource_show', {'id': resource_id})


def get_record(resource_id, record_id):
    return _get_action('record_get', {'resource_id': resource_id, 'record_id': record_id})


def resource_view_get_ordered_fields(resource_id):
    """
    This is a replacement for resource_view_get_fields, but this function
    handles errors internally, and return the fields in their original order
    @param resource_id:
    @return:
    """
    return resource_get_ordered_fields(resource_id)


def form_select_datastore_field_options(resource_id=None, allow_empty=False):

    # Need to check for resource_id as this form gets loaded on add, nut just edit
    # And on add there will be no resource_id
    if resource_id:
        datastore_fields = resource_get_ordered_fields(resource_id)
        return list_to_form_options(datastore_fields, allow_empty)

    return []


def form_select_update_frequency_options():
    """
    Get update frequencies as a form list
    @return:
    """
    return list_to_form_options(UPDATE_FREQUENCIES)


def update_frequency_get_label(value):
    """
    Get the label for this update frequency
    @param value:
    @return:
    """
    for v, label in UPDATE_FREQUENCIES:
        if v == value:
            return label

def dataset_types():
    """
    Return list of dataset category terms
    @return: list
    """
    try:
        return toolkit.get_action('tag_list')(data_dict={'vocabulary_id': DATASET_TYPE_VOCABULARY})
    except toolkit.ObjectNotFound:
        return []


def url_for_collection_view(view_type='recline_grid_view', filters={}):
    """
    Return URL to link through to specimen dataset view, with optional search params
    @param view_type: grid to link to - grid or map
    @param kwargs: search filter params
    @return: url
    """

    resource_id = get_specimen_resource_id()
    context = {'model': model, 'session': model.Session, 'user': c.user}

    try:
        views = toolkit.get_action('resource_view_list')(context, {'id': resource_id})
    except NotFound:
        return None
    else:

        for view in views:
            if view['view_type'] == view_type:
                break

        filters = '|'.join(['%s:%s' % (k, v) for k, v in filters.items()])

        return url_for(controller='package', action='resource_read', id=view['package_id'], resource_id=view['resource_id'], view_id=view['id'], filters=filters)


def url_for_indexlot_view():
    return ''


def indexlot_count():
    return delimit_number(700000)


def get_nhm_organisation_id():
    """
    @return:  ID for the NHM organisation
    """
    return config.get("ldap.organization.id")


def get_specimen_resource_id():
    """
    @return:  ID for the specimen resource
    """
    return


def get_indexlot_resource_id():
    """
    @return:  ID for indexlot resource
    """
    return


@cache_region('short_term', 'collection_stats')
def collection_stats():
    """
    Get collection stats, grouped by Collection code
    @return:
    """

    resource_id = get_specimen_resource_id()

    if not resource_id:
        log.error('Please configure collection resource ID')

    context = {'model': model, 'session': model.Session, 'user': c.user}

    sql = '''SELECT "Collection code", COUNT(*) AS count
           FROM "{resource_id}"
           GROUP BY "Collection code" ORDER BY count DESC'''.format(resource_id=resource_id)

    total = 0
    collections = OrderedDict()

    try:
        result = toolkit.get_action('datastore_search_sql')(context, {'sql': sql})
    except ValidationError, e:
        log.critical('Error retrieving collection statistics %s', e)
    else:

        for record in result['records']:
            count = int(record['count'])
            collections[record['Collection code']] = count
            total += count

    stats = {
        'total': total,
        'collections': collections
    }

    return stats


def get_department(collection_code):
    """
    Return a department name for collection code
    @param collection_code: BOT, PAL etc.,
    @return: Full department name - Entomology
    """
    departments = {
        'BMNH(E)': 'Entomology',
        'BOT': 'Botany',
        'MIN': 'Mineralogy',
        'PAL': 'Palaeontology',
        'ZOO': 'Zoology',
    }

    return departments[collection_code]


def delimit_number(num):
    """
    Separate long number into thousands 1000000 => 1,000,000
    @param num:
    @return:
    """
    return "{:,}".format(num)


def api_doc_link():
    """
    Link to API documentation
    @return:
    """
    attr= {'class': 'external', 'target': '_blank'}
    # TODO: Change to http://docs.nhm.apiary.io/
    return link_to(_('API Docs'), 'http://docs.ckan.org/en/latest/api/index.html', **attr)


def get_google_analytics_config():
    """
    Get Google Analytic configuration
    @return:
    """

    return {
        'id': config.get("googleanalytics.id"),
        'domain': config.get("googleanalytics.domain", "auto")
    }


def persistent_follow_button(obj_type, obj_id):
    '''Return a follow button for the given object type and id.

    Replaces ckan.lib.follow_button which returns an empty string for anonymous users

    For anon users this function outputs a follow button which links through to the login page

    '''
    obj_type = obj_type.lower()
    assert obj_type in _follow_objects

    if c.user:
        context = {'model': model, 'session': model.Session, 'user': c.user}
        action = 'am_following_%s' % obj_type
        following = logic.get_action(action)(context, {'id': obj_id})
        return snippet('snippets/follow_button.html',
                   following=following,
                   obj_id=obj_id,
                   obj_type=obj_type)

    return snippet('snippets/anon_follow_button.html',
           obj_id=obj_id,
           obj_type=obj_type)


def filter_resource_items(key):
    """
    Filter resource items - if key is in blacklist, return false
    @param key:
    @return: boolean
    """

    blacklist = ['image field', 'title field', 'datastore active', 'has views', 'on same domain', 'resource group id', 'revision id', 'url type']

    return key.strip() not in blacklist


def get_map_styles():
    """
    New map config overriding the marker point img
    @return:
    """
    return {
        'point': {
            'iconUrl': '/images/leaflet/marker.png',
            'iconSize': [20, 34],
            'iconAnchor': [12, 30]
        }
    }


def get_query_params():
    """
    Helper function to build a dict of query params
    To be used in urls for persistent filters
    @return: dict
    """
    params = dict()

    for key in ['q', 'filters']:
        value = request.params.get(key)
        if value:
            params[key] = value

    return params


def resource_view_get_view(resource):
    """
    Retrieve the controller for a resource
    Try and match on resource ID, or on format
    So we can provide a custom controller for all format types - e.g. DwC
    @param resource:
    @return: controller class
    """

    subclasses = DefaultView.__subclasses__()

    for cls in subclasses:
        # Does the resource ID match the record controller
        if cls.resource_id == resource['id']:
            return cls()

    # Or do we have a controller for a particular format type (eg. DwC)
    # Run in separate loop so this is lower specificity
    for cls in subclasses:
        if cls.format == resource['format']:
            return cls()

    return DefaultView()


def resource_view_get_field_groups(resource):
    """
    Return dictionary of field groups

    @param resource: resource dict
    @return: OrderedDict of fields
    """
    view_cls = resource_view_get_view(resource)

    return view_cls.get_field_groups(resource)


# Resource view and filters
def resource_view_state(resource_view_json, resource_json):
    """
    Alter the recline view resource, adding in state info
    @param resource_view_json:
    @return:
    """
    resource_view = json.loads(resource_view_json)
    resource = json.loads(resource_json)

    # There is an annoying feature/bug in slickgrid, that if fitColumns=True
    # And grid is wider than available viewport, slickgrid columns cannot
    # Be resized until fitColumns is deactivated
    # So to fix, we're going to work out how many columns are in the dataset
    # To decide whether or not to turn on fitColumns
    # Messy, but better than trying to hack around with slickgrid

    resource_fields = resource_get_ordered_fields(resource_view['resource_id'])

    # Add hidden fields
    # The way Slickgrid is implemented, we cannot pass in an array of columns
    # Instead if display fields is set, we will mark all other columns as hidden
    hidden_fields = resource_view_get_hidden_fields(resource)

    num_fields = len(resource_fields) - len(hidden_fields)

    viewport_max_width = 920
    col_width = 100
    fit_columns = (num_fields * col_width) < viewport_max_width

    resource_view['state'] = {
        'fitColumns': fit_columns,
        'gridOptions': {
            'defaultFormatter': 'NHMFormatter',
            'enableCellRangeSelection': False,
            'enableTextSelectionOnCells': False,
            'enableCellNavigation': False,
            'enableColumnReorder': False,
            'defaultColumnWidth': 100
        },
        'columnsWidth': [
            {
                'column': '_id',
                'width': 45
            },
        ],
        'columnsTitle': [
            {
                'column': '_id',
                'title': ''  # This is just converted into a link so lets hide the field
            }
        ],
        'columnsToolTip': []
    }

    for group, fields in resource_view_get_field_groups(resource).items():

        for field, label in fields.items():

            if field in resource_fields:

                # If we have a group, add a tooltip
                # Otherwise will use title text
                if group:
                    resource_view['state']['columnsToolTip'].append(
                        {
                            'column': field,
                            'value': '%s: %s' % (group, label)
                        }
                    )

                # Add custom titles
                resource_view['state']['columnsTitle'].append(
                    {
                        'column': field,
                        'title': label
                    }
                )

    # Do we have custom column widths set in the controller
    view_cls = resource_view_get_view(resource)
    if view_cls.grid_column_widths:
        for column, width in view_cls.grid_column_widths.items():
            resource_view['state']['columnsWidth'].append(
                {
                    'column': column,
                    'width': width
                }
            )

    if hidden_fields:
        resource_filter_set_cookie(resource_view['resource_id'], hidden_fields)
        resource_view['state']['hiddenColumns'] = hidden_fields
    else:
        resource_filter_delete_cookie(resource_view['resource_id'])

    return json.dumps(resource_view)


def resource_is_dwc(resource):
    """
    Is the resource format DwC?
    @param resource:
    @return:
    """
    return bool(resource.get('format').lower() == 'dwc')


def resource_view_get_hidden_fields(resource):
    """
    Get a list of hidden fields
    This is called from resource_view_filters.html and helper resource_view_state
    So the same fields are hidden in the form and Slickgrid

    @param resource id:
    @return: list of hidden fields
    """

    """
    Parse hidden fields from the filter dictionary
    @param filter_dict:
    """

    filter_dict = parse_request_filters()

    # Get all display fields explicitly set
    display_fields = filter_dict.pop(FIELD_DISPLAY_FILTER, [])

    # Load the hidden fields cookie
    # hidden_fields_cookie = resource_filter_get_cookie(resource['id'])

    # TEMP: Just for debugging
    hidden_fields_cookie = None

    # Retrieve the fields for this resource
    resource_fields = resource_get_ordered_fields(resource['id'])

    # If user has set display fields, loop through display fields
    # And available fields, to build a list of hidden fields
    if display_fields:

        # Ensure it's a list
        if not isinstance(display_fields, list):
            display_fields = [display_fields]

        # Make sure _id is never hidden
        display_fields.append('_id')

        # Make sure all filtered fields are never hidden
        display_fields += filter_dict.keys()

        # Hidden fields are all other resource fields not in the display field array
        return list(set(resource_fields) - set(display_fields))

    elif hidden_fields_cookie:

        # Make sure that even if we're using the hidden fields cookie
        # All filtered fields are removed from the hidden field list
        hidden_fields_cookie = list(set(hidden_fields_cookie) - set(filter_dict.keys()))
        return hidden_fields_cookie

    else:

        # User has nto customised the grid - so see if we have custom display
        # fields set in the controller
        view_cls = resource_view_get_view(resource)

        if view_cls.grid_default_columns:
            return [f for f in resource_fields if f not in view_cls.grid_default_columns]

    return {}


def get_resource_filter_options(resource):
    """Return the available filter options for the given resource

    @type resource: dict
    @param resource: Dictionary representing a resource
    @rtype: dict
    @return: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - checked: True if the option is currently applied.
    """
    options = resource_filter_options(resource)
    filter_list = toolkit.request.params.get('filters', '').split('|')
    filters = {}
    for filter_def in filter_list:
        try:
            (key, value) = filter_def.split(':', 1)
        except ValueError:
            continue
        if key not in filters:
            filters[key] = [value]
        else:
            filters[key].append(value)
    for o in options:
        if o in filters and 'true' in filters[o]:
            options[o]['checked'] = True
        else:
            options[o]['checked'] = False
    return options


def get_resource_filter_pills(resource):
    """
    Get filter pills
    We don't want the field group pills - these are handled separately in get_resource_field_groups
    @param resource:
    @return:
    """

    filter_dict = parse_request_filters()

    def get_pill_filters(exclude_field, exclude_value):
        """
        Build filter, using filters which aren't exclude_field=exclude_value
        @param exclude_field:
        @param exclude_value:
        @return:
        """

        filters = []
        for field, values in filter_dict.items():
            for value in values:
                if not (field == exclude_field and value == exclude_value):
                    filters.append('%s:%s' % (field, value))

        return '|'.join(filters)

    pills = {}

    options = resource_filter_options(resource)

    field_labels = {}

    field_groups = resource_view_get_field_groups(resource)

    if field_groups:
        for fields in field_groups.values():
            for field_name, label in fields.items():
                field_labels[field_name] = label

    for field, values in filter_dict.items():
        for value in values:
            filters = get_pill_filters(field, value)

            # If this is the _tmgeom field, we don't want to output the whole value as it's in the format:
            # POLYGON ((-100.45898437499999 41.902277040963696, -100.45898437499999 47.54687159892238, -92.6806640625 47.54687159892238, -92.6806640625 41.902277040963696, -100.45898437499999 41.902277040963696))
            if field == '_tmgeom':
                pills['geometry'] = {'Polygon': filters}
            elif field in options:
                label = options[field]['label']
                try:
                    pills['Options'][label] = filters
                except KeyError:
                    pills['Options'] = {label: filters}
            else:

                try:
                    label = field_labels[field]
                except KeyError:
                    label = field

                try:
                    pills[label][value] = filters
                except KeyError:
                    pills[label] = {value: filters}

    # Remove the field group key, if it exists
    pills.pop(FIELD_DISPLAY_FILTER, None)
    return pills


def get_allowed_view_types(resource, package):
    """
    Overwrite ckan.lib.helpers.get_allowed_view_types
    We want to edit some of the options - remove Image and change Tiled Map to Map
    @param resource:
    @param package:
    @return:
    """

    view_types = ckan_get_allowed_view_types(resource, package)
    blacklisted_types = ['image']

    filtered_types = []

    for view_type in view_types:
        # Exclude blacklisted types (at the moment just Image)
        if view_type[0] in blacklisted_types:
            continue

        # Rename Tiled map => map
        if view_type[1] == 'Tiled map':
            view_type = (view_type[0], 'Map', view_type[2])

        filtered_types.append(view_type)

    return filtered_types


def get_facet_label_function(facet_name, multi=False):
    """For a given facet, return the function used to fetch the facet's items labels

    @param facet_name: Facet name
    @param multi: If True, the function returned should take a list of facets and a filter value to find the matching
                  facet on the name field
    @return: A function or None
    """
    facet_function = None
    if facet_name == 'creator_user_id':
        facet_function = get_creator_id_facet_label

    if facet_function and multi:
        def filter_facets(facet, filter_value):
            for f in facet:
                if f['name'] == filter_value:
                    return facet_function(f)
            return filter
        return filter_facets
    else:
        return facet_function


def get_creator_id_facet_label(facet):
    """Return display name for the creator_id facet

    @param facet: A dictionary representing a single value for the facet
    @return: A string to use for display name
    """
    try:
        user = model.User.get(facet['name'])
        display_name = user.display_name
    except (NotFound, AttributeError) as e:
        display_name = facet['display_name']
    return display_name


def field_name_label(field_name):
    """
    Convert a field name into a label - replacing _s and upper casing first character
    @param field:
    @return: str label
    """
    label = field_name.replace('_', ' ')
    label = label[0].upper() + label[1:]
    return label


def get_contact_form_params(pkg=None, res=None, rec=None):
    """
    Get a list of IDS

    @param pkg:
    @param res:
    @param rec:
    @return:
    """

    params = {}

    if pkg:
        params['package_id'] = pkg.get('id')

    if res:
        params['resource_id'] = res.get('id')

    if rec:
        params['record_id'] = rec.get('_id')

    return params


def get_contact_form_template_url(params):
    """
    Build a URL suitable for linking to the contact form snippet

    For example: /api/1/util/snippet/contact_form.html?resource_id=123&record_id456

    Can be parsed output from get_contact_form_params

    @param params:
    @return:
    """

    url = '/api/1/util/snippet/contact_form.html'

    if params:
        url += '?%s' % urllib.urlencode(params)

    return url

def downloadable(resource):
    """
    Is a resource downloadable
    @param resource:
    @return: bool
    """
    return bool(resource['format'])

def is_sysadmin():
    """
    Is user a sysadmin user
    @return:
    """
    if c.userobj.sysadmin:
        return True

def record_display_field(field_name, value):
    """
    Decide whether to display a field
    Evaluates whether a field has value
    @param field_name:
    @param value:
    @return: bool - true to display field; false not to
    """

    # If this is a string, strip it before evaluating
    if isinstance(value, basestring):
        value = value.strip()

    return bool(value)


def group_fields_have_data(record_dict, fields):
    """
    Are any of the fields in the group populated
    Return true if they are; false if not
    @param record_dict: record data
    @param fields: fields to test
    @return: bool
    """

    for field in fields:
        if record_dict.get(field, None):
            return True


def indexlot_material_details(record_dict):
    """
    Parse the material details into an array, with first column the header
    @param record_dict:
    @return:
    """

    material_details = []

    material_detail_fields = [
        'Material count',
        'Material sex',
        'Material stage',
        'Material types',
        'Material primary type no'
    ]

    # Create a list of lists, containing field and values
    # First row will be field title
    for material_detail_field in material_detail_fields:
        if record_dict[material_detail_field]:
            field_values = record_dict[material_detail_field].split(';')
            if field_values:
                label = material_detail_field.replace('Material', '').strip().capitalize()
                material_details.append([label] + field_values)

    # Transpose list of values & fill in missing values so they are all the same length
    if material_details:
        material_details = map(lambda *row: list(row), *material_details)

    return material_details


def get_image_licence_options():
    """
    Return list of image licences
    Currently this is the same list as dataset licences
    @return:
    """

    licenses = [('', '')] + model.Package.get_license_options()

    # Format licences as form options list of dicts
    return [{'value': value, 'text': text} for text, value in licenses]


def social_share_text(pkg_dict=None, res_dict=None, rec_dict=None):
    """
    Generate social share text for a package
    @param pkg_dict:
    @return:
    """

    text = list()

    if rec_dict:
        text.append(rec_dict.get(res_dict['_title_field'], 'Record %s' % rec_dict['_id']))
    elif res_dict:
        text.append('%s' % (res_dict['name']))
    elif pkg_dict:
        text.append('%s' % (pkg_dict['title'] or pkg_dict['name']))

    text.append('on the @NHM_London Data Portal')

    text.append('DOI: %s' % os.path.join('http://dx.doi.org', pkg_dict['doi']))

    return ' '.join(text)