import json
import logging
import urllib
from collections import defaultdict, OrderedDict
from operator import itemgetter

import os
import re
from beaker.cache import cache_region
from jinja2.filters import do_truncate
from pylons import config
from webhelpers.html import literal

import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.common import c, _, request
from ckan.lib import helpers as h
from ckan.lib.helpers import format_resource_items
from ckanext.gbif.lib.errors import GBIF_ERRORS
from ckanext.nhm.lib import external_links
from ckanext.nhm.lib.form import list_to_form_options
from ckanext.nhm.lib.resource_view import resource_view_get_view, resource_view_get_filter_options
from ckanext.nhm.lib.taxonomy import extract_ranks
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY, UPDATE_FREQUENCIES
from ckanext.nhm.settings import COLLECTION_CONTACTS

log = logging.getLogger(__name__)

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

get_action = logic.get_action
_check_access = logic.check_access

# Make enumerate available to templates
enumerate = enumerate

re_dwc_field_label = re.compile('([A-Z]+)')

re_url_validation = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Maximum number of characters for the author string
AUTHOR_MAX_LENGTH = 100


@cache_region('permanent', 'collection_stats')
def get_site_statistics():
    stats = dict()
    stats['dataset_count'] = logic.get_action('package_search')({}, {"rows": 1})['count']
    # Get a count of all distinct user IDs
    stats['contributor_count'] = get_contributor_count()
    record_count = 0
    try:
        dataset_statistics = _get_action('dataset_statistics', {})
        record_count = dataset_statistics.get('total', 0)
    except Exception as _e:
        # if there was a problem getting the stats return 0 and log an exception
        log.exception('Could not gather dataset statistics')
    stats['record_count'] = record_count
    return stats


def get_contributor_count():
    return model.Session.execute("SELECT COUNT(DISTINCT creator_user_id) FROM package WHERE state='active'").scalar()


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
    record = _get_action('record_show', {'resource_id': resource_id, 'record_id': record_id})
    return record.get('data', None)


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


def dataset_categories():
    """
    Return list of dataset category terms
    @return: list
    """
    try:
        return toolkit.get_action('tag_list')(data_dict={'vocabulary_id': DATASET_TYPE_VOCABULARY})
    except toolkit.ObjectNotFound:
        return []


def url_for_collection_view(view_type=None, filters={}):
    """
    Return URL to link through to specimen dataset view, with optional search params
    @param view_type: grid to link to - grid or map
    @param kwargs: search filter params
    @return: url
    """
    resource_id = get_specimen_resource_id()
    return url_for_resource_view(resource_id, view_type, filters)


def url_for_indexlot_view():
    """
    Return URL to link through to index lot resource view
    @return: url
    """
    resource_id = get_indexlot_resource_id()
    return url_for_resource_view(resource_id)


def url_for_resource_view(resource_id, view_type=None, filters={}):
    """
    Get URL to link to resource view
    If no view type is specified, the first view will be used
    @param resource_id:
    @param view_type:
    @param filters:
    @return:
    """
    context = {'model': model, 'session': model.Session, 'user': c.user}

    try:
        views = toolkit.get_action('resource_view_list')(context, {'id': resource_id})
    except NotFound:
        return None
    else:
        if not views:
            return None

        if not view_type:
            view = views[0]
        else:
            for view in views:
                if view['view_type'] == view_type:
                    break

        filters = '|'.join(['%s:%s' % (k, v) for k, v in filters.items()])

        return h.url_for(controller='package', action='resource_read', id=view['package_id'], resource_id=view['resource_id'], view_id=view['id'], filters=filters)


@cache_region('permanent', 'collection_stats')
def indexlot_count():
    resource_id = get_indexlot_resource_id()

    if not resource_id:
        log.error('Please configure index lot resource ID')

    context = {'model': model, 'session': model.Session, 'user': c.user}

    search_params = dict(
        resource_id=resource_id,
        limit=1,
    )
    search = logic.get_action('datastore_search')(context, search_params)
    return delimit_number(search.get('total', 0))


def get_nhm_organisation_id():
    """
    @return:  ID for the NHM organisation
    """
    return config.get("ldap.organization.id")


def get_specimen_resource_id():
    """
    @return:  ID for the specimen resource
    """
    return config.get("ckanext.nhm.specimen_resource_id")


def get_indexlot_resource_id():
    """
    @return:  ID for indexlot resource
    """
    return config.get("ckanext.nhm.indexlot_resource_id")


@cache_region('permanent', 'collection_stats')
def collection_stats():
    """
    Get collection stats, grouped by Collection code
    @return:
    """
    resource_id = get_specimen_resource_id()
    total = 0
    collections = OrderedDict()
    search_params = dict(
        resource_id=resource_id,
        # use limit 0 as we're not interested in getting any results, just the facet counts
        limit=0,
        facets=[u'collectionCode'],
    )

    result = logic.get_action(u'datastore_search')({}, search_params)
    for collection_code, num in result[u'facets'][u'collectionCode']['values'].items():
        collections[collection_code] = num
        total += num

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
        'bmnh(e)': 'Entomology',
        'bot': 'Botany',
        'min': 'Mineralogy',
        'pal': 'Palaeontology',
        'zoo': 'Zoology',
    }

    return departments[collection_code.lower()]


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
    attr = {'class': 'external', 'target': '_blank'}
    return h.link_to(_('API guide'), 'http://docs.ckan.org/en/latest/api/index.html', **attr)


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
    assert obj_type in h._follow_objects

    if c.user:
        context = {'model': model, 'session': model.Session, 'user': c.user}
        action = 'am_following_%s' % obj_type
        following = logic.get_action(action)(context, {'id': obj_id})
        return h.snippet('snippets/follow_button.html',
                         following=following,
                         obj_id=obj_id,
                         obj_type=obj_type)

    return h.snippet('snippets/anon_follow_button.html',
                     obj_id=obj_id,
                     obj_type=obj_type)


def filter_and_format_resource_items(resource):
    '''
    Given a resource, return the items from it that are whitelisted for display and format them.

    :param resource: the resource dict
    :return: a list of made up of 2-tuples containing formatted keys and values from the resource
    '''
    blacklist = {'_image_field', '_title_field', 'datastore_active', 'has_views',
                 'on_same_domain', 'resource_group_id', 'revision_id', 'url_type'}
    items = []
    for key, value in resource.items():
        if key not in blacklist:
            items.append((key, value))
    return format_resource_items(items)


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

    fields = h.resource_view_get_fields(resource)

    num_fields = len(fields)

    viewport_max_width = 920
    col_width = 100
    fit_columns = (num_fields * col_width) < viewport_max_width

    # Initiate the resource view
    view = resource_view_get_view(resource)

    # And get the state
    resource_view['state'] = view.get_slickgrid_state()

    # TODO: This can be merged into get_slickgrid_state
    resource_view['state']['fitColumns'] = fit_columns

    # ID and DQI always first
    columns_order = ['_id']
    if 'gbifIssue' in fields:
        columns_order.append('gbifIssue')
    # Add the rest of the columns to the columns order
    columns_order += [f for f in fields if f not in columns_order]
    resource_view['state']['columnsOrder'] = list(columns_order)

    if view.grid_column_widths:
        for column, width in view.grid_column_widths.items():
            resource_view['state']['columnsWidth'].append(
                {
                    'column': column,
                    'width': width
                }
            )

    try:
        return json.dumps(resource_view)
    except TypeError:
        return {}


def resource_is_dwc(resource):
    """
    Is the resource format DwC?
    @param resource:
    @return:
    """
    return bool(resource.get('format').lower() == 'dwc')


def camel_case_to_string(camel_case_string):
    s = ' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', camel_case_string))
    return s[0].upper() + s[1:]


def get_resource_filter_options(resource, resource_view):
    """Return the available filter options for the given resource

    @type resource: dict
    @param resource: Dictionary representing a resource
    @rtype: dict
    @return: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - checked: True if the option is currently applied.
    """
    options = resource_view_get_filter_options(resource)
    filter_list = toolkit.request.params.get('filters', '').split('|')
    filters = {}

    # If this is a gallery view, hide the has image filter
    # Only records with images will be displayed anyway
    # if resource_view['view_type'] == 'gallery':
    #     options.pop("_has_image", None)

    for filter_def in filter_list:
        try:
            (key, value) = filter_def.split(':', 1)
        except ValueError:
            continue

        if key not in filters:
            filters[key] = [value]
        else:
            filters[key].append(value)
    result = {}
    for option in options:
        if option.hide:
            continue
        result[option.name] = option.as_dict()
        result[option.name]['checked'] = option.name in filters and 'true' in filters[option.name]
    return result


def get_resource_gbif_errors(resource):
    """
    Return GBIF errors applicable for this resource
    i.e. if this the specimen resource, return the gbif errors dict
    :param resource:
    :return:
    """

    # If this is a
    if resource.get('id') == get_specimen_resource_id():
        return GBIF_ERRORS
    else:
        return {}


def get_allowed_view_types(resource, package):
    """
    Overwrite ckan.lib.helpers.get_allowed_view_types
    We want to edit some of the options - remove Image and change Tiled Map to Map
    @param resource:
    @param package:
    @return:
    """

    view_types = h.get_allowed_view_types(resource, package)
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


def field_is_link(value):
    """
    Is a field a link (starts with http and is a valid URL)
    @param value:
    @return: boolean
    """
    try:
        return value.startswith('http') and re_url_validation.match(value)
    except Exception:
        pass
    return False


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


def get_contact_form_department_options():
    """
    Contact form category
    @return:
    """
    return list_to_form_options(COLLECTION_CONTACTS.keys())


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
    text = []
    if rec_dict:
        title_field = res_dict.get(u'_title_field', None)
        if title_field and rec_dict.get(title_field, None):
            text.append(rec_dict[title_field])
        else:
            text.append(u'Record {}'.format(rec_dict[u'_id']))
    elif res_dict:
        text.append(res_dict[u'name'])
    elif pkg_dict:
        text.append(pkg_dict[u'title'] or pkg_dict[u'name'])

    text.append(u'on the @NHM_London Data Portal')

    try:
        text.append(u'DOI: %s' % os.path.join(u'https://doi.org', pkg_dict[u'doi']))
    except KeyError:
        pass

    return urllib.quote(u' '.join(map(unicode, text)).encode(u'utf8'))


def accessible_gravatar(email_hash, size=100, default=None, userobj=None):
    """
    Port of ckan helper gravatar
    Adds title text to the image so it passes accessibility checks
    @param email_hash:
    @param size:
    @param default:
    @param userobj:
    @return:
    """
    if default is None:
        default = config.get('ckan.gravatar_default', 'identicon')

    if not default in h._VALID_GRAVATAR_DEFAULTS:
        # treat the default as a url
        default = urllib.quote(default, safe='')

    return literal('''<img alt="%s" src="//gravatar.com/avatar/%s?s=%d&amp;d=%s"
        class="gravatar" width="%s" height="%s" />'''
                   % (userobj.name, email_hash, size, default, size, size)
                   )


def dataset_author_truncate(author_str):
    """

    For author strings with lots of authors need to shorten for display
    insert et al as abbreviation tag

    @param author_str: dataset author
    @return: shortened author str, will full text in abbr tag
    """

    def _truncate(author_str, separator=None):

        # If we have a separator, split string on it
        if separator:
            shortened = ';'.join(author_str.split(separator)[0:4])
        else:
            # Otherwise use the jinja truncate function (may split author name)
            shortened = do_truncate(author_str, length=AUTHOR_MAX_LENGTH, end='')

        return literal(u'{0} <abbr title="{1}" style="cursor: pointer;">et al.</abbr>'.format(shortened, author_str))

    if author_str and len(author_str) > AUTHOR_MAX_LENGTH:

        if ';' in author_str:
            author_str = _truncate(author_str, ';')
        elif ',' in author_str:
            author_str = _truncate(author_str, ',')
        else:
            author_str = _truncate(author_str)

    return author_str


def get_resource_facets(resource):
    """
    Return a list of facets for a particular resource
    @param resource:
    @return:
    """
    resource_view = resource_view_get_view(resource)
    # if facets aren't defined in the resource view, then just return
    if not resource_view.field_facets:
        return
    # Build query parameters for the faceted search. We'll use the same query parameters used in the
    # current request and then add extras to perform a faceted query, returning facets but zero
    # results (limit=0)
    query_params = get_query_params()

    # Convert filters to a dictionary as this won't happen automatically
    # as we're retrieving raw get parameters from get_query_params
    filters = {}
    if query_params.get('filters'):
        for f in query_params.get('filters').split('|'):
            filter_field, filter_value = f.split(':', 1)
            filters[filter_field] = filter_value

    search_params = dict(
        resource_id=resource.get('id'),
        # use limit 0 as we're not interested in getting any results, just the facets
        limit=0,
        facets=resource_view.field_facets,
        q=query_params.get('q', None),
        filters=filters,
    )

    # if the show more button is clicked, a parameter is added to the query which informs us we need
    # to show more facets, so use 50 for the facet limit on the given field
    for field_name in resource_view.field_facets:
        if h.get_param_int(u'_{}_limit'.format(field_name)) == 0:
            search_params.setdefault(u'facet_limits', {})[field_name] = 50

    search = logic.get_action('datastore_search')({}, search_params)
    facets = []

    # dictionary of facet name => formatter function with camel_case_to_string defined as the
    # default formatting function and then any overrides for specific edge cases
    facet_label_formatters = defaultdict(lambda: camel_case_to_string, **{
        # specific lambda for GBIF to ensure it's capitalised correctly
        'gbifIssue': lambda _: 'GBIF Issue'
    })

    # Dictionary of field name => formatter function
    # Pass facet value to a formatter to get a better facet item label, if the facet doesn't have a
    # formatter defined then the value is just used as is
    facet_field_label_formatters = defaultdict(lambda: (lambda v: v.capitalize()), **{
        'collectionCode': get_department
    })

    # Loop through original facets to ensure order is preserved
    for field_name in resource_view.field_facets:
        # parse the facets into a list of dictionary values
        facets.append({
            'name': field_name,
            'label': facet_label_formatters[field_name](field_name),
            'has_more': search['facets'][field_name]['details']['sum_other_doc_count'] > 0,
            'active': field_name in filters,
            'facet_values': [
                {
                    'name': value,
                    'label': facet_field_label_formatters[field_name](value),
                    'count': count
                    # loop over the top values, sorted by count desc so that the top value is first
                } for value, count in sorted(search['facets'][field_name]['values'].items(),
                                             key=itemgetter(1), reverse=True)
            ]
        })

    return facets


def remove_url_filter(field, value, extras=None):
    """
    The CKAN built in functions remove_url_param / add_url_param cannot handle
    multiple filters which are concatenated with |, not separate query params
    This replaces remove_url_param for filters
    @param field:
    @param value:
    @param extras:
    @return:
    """

    # import copy
    # params = copy.copy(dict(request.params))

    params = dict(request.params)
    try:
        del params['filters']
    except KeyError:
        pass
    else:
        filters = parse_request_filters()
        if field in filters:
            # Convert all filters to unicode for ease of comparison
            filters[field] = map(unicode.lower, filters[field])
            # Remove the filter value form the current filters
            value_list = value if isinstance(value, list) else [value]
            for value_item in value_list:
                try:
                    # Try and remove the item from the filters
                    filters[field].remove(value_item.lower())
                except ValueError:
                    continue

            # If the filters values for the field are empty, remove the whole field
            if not filters[field]:
                del filters[field]

        # Combine the filters again
        filter_parts = []
        for filter_field, filter_values in filters.items():
            for filter_value in filter_values:
                filter_parts.append('%s:%s' % (filter_field, filter_value))
        # If we have filter parts, add them back to the params dict
        if filter_parts:
            params['filters'] = '|'.join(filter_parts)
    return _create_filter_url(params, extras)


def add_url_filter(field, value, extras=None):
    """
    The CKAN built in functions remove_url_param / add_url_param cannot handle
    multiple filters which are concatenated with |, not separate query params
    This replaces remove_url_param for filters
    @param field:
    @param field:
    @param extras:
    @return:
    """

    params = dict(request.params)
    url_filter = '%s:%s' % (field, value)
    if params.get('filters', None):
        params['filters'] += '|%s' % url_filter
    else:
        params['filters'] = url_filter

    return _create_filter_url(params, extras)


def _create_filter_url(params, extras=None):
    """
    Helper function to create filter URL
    @param params:
    @param extras:
    @return:
    """
    params_no_page = [(k, v) for k, v in params.items() if k != 'page']
    return h._create_url_with_params(list(params_no_page), extras=extras)


def parse_request_filters():
    """
    Get the filters from the request object
    @return:
    """
    filter_dict = {}

    try:
        filter_params = request.params.get('filters').split('|')
    except AttributeError:
        return {}

    # Remove empty values form the filter_params
    filter_params = filter(None, filter_params)

    for filter_param in filter_params:
        field, value = filter_param.split(':', 1)
        filter_dict.setdefault(field, []).append(value)

    return filter_dict


def get_resource_filter_pills(package, resource, resource_view=None):
    """
    Get filter pills
    We don't want the field group pills - these are handled separately in get_resource_field_groups
    @param resource:
    @param package:
    @return:
    """

    filter_dict = parse_request_filters()
    extras = {
        'id': package['id'],
        'resource_id': resource['id']
    }

    pills = []

    for filter_field, filter_value in filter_dict.items():
        # If the field name stars with an underscore, don't include it in the pills
        if filter_field.startswith('_'):
            continue
        # Remove filter from url function
        href = remove_url_filter(filter_field, filter_value, extras=extras)
        pills.append({
            'label': camel_case_to_string(filter_field),
            'field': filter_field,
            'value': ' '.join(filter_value),
            'href': href
        })

    return pills


def resource_view_get_filterable_fields(resource):
    """

    @return:
    """

    filterable_field_types = ['int', 'text', 'numeric']

    if not resource.get('datastore_active'):
        return []

    data = {
        'resource_id': resource['id'],
        'limit': 0,
        # As these are for the filters, only get the indexed fields
        'indexed_only': True
    }

    result = logic.get_action('datastore_search')({}, data)

    fields = [f['id'] for f in result.get('fields', []) if f['type'] in filterable_field_types]
    return sorted(fields)


def form_select_datastore_field_options(resource, allow_empty=True):
    fields = h.resource_view_get_fields(resource)
    return list_to_form_options(fields, allow_empty)


def get_last_resource_update_for_package(pkg_dict, date_format=None):
    '''
    Returns the most recent update datetime across all resources in this
    package. If there is no update time found then 'unknown' is returned. If
    there is datetime found then it is rendered using the standard ckan helper.
    :param pkg_dict:        the package dict
    :param date_format:     date format for the return datetime
    :return: 'unknown' or a string containing the rendered datetime and the
    resource name
    '''

    def get_resource_last_update(resource):
        '''
        Given a resource dict, return the most recent update time available from
        it, or None if there is no update time.
        :param resource:    the resource dict
        :return: a datetime or None
        '''
        # a list of fields on the resource that should contain update dates
        fields = [u'last_modified', u'revision_timestamp', u'Created']
        # find the available update dates on the resource and filter out Nones
        update_dates = filter(None, [h._datestamp_to_datetime(resource[field]) for field in fields])
        # return the latest non-None value, or None
        return max(update_dates) if update_dates else None

    # find the latest update date for each resource using the above function and
    # then filter out the ones that don't have an update date available
    dates_and_names = filter(lambda x: x[0],
                             [(get_resource_last_update(r), r['name']) for r in pkg_dict[u'resources']])
    if dates_and_names:
        # find the most recent date and name combo
        date, name = max(dates_and_names, key=lambda x: x[0])
        return '{} ({})'.format(h.render_datetime(date, date_format=date_format), name)
    # there is no available update so we return 'unknown'
    return _('unknown')


def get_external_links(record):
    '''
    Helper called on collection record pages (i.e. records in the specimens, indexlots or artefacts resources) which is
    expected to return a list of tuples. Each tuple provides a title and a list of links, respectively, which are
    relevant to the record.
    :param record:
    :return:
    '''
    sites = external_links.get_relevant_sites(record)
    ranks = extract_ranks(record)
    if ranks:
        return [(name, icon, OrderedDict.fromkeys([(rank, link.format(rank)) for rank in ranks.values()]))
                for name, icon, link in sites]
    return []
