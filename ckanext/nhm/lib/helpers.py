#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import itertools
import json
import logging
import operator
import re
import time
from collections import OrderedDict, defaultdict
from datetime import datetime
from operator import itemgetter
from typing import List
from urllib.parse import quote

from beaker.cache import cache_region
from jinja2.filters import do_truncate
from lxml import etree, html

from ckan import model
from ckan.lib import helpers as core_helpers
from ckan.lib.helpers import literal
from ckan.plugins import toolkit
from ckanext.gbif.lib.errors import GBIF_ERRORS
from ckanext.nhm.lib import external_links
from ckanext.nhm.lib.external_links import Site
from ckanext.nhm.lib.form import list_to_form_options
from ckanext.nhm.lib.resource_view import (
    resource_view_get_filter_options,
    resource_view_get_view,
)
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY, UPDATE_FREQUENCIES
from ckanext.nhm.settings import COLLECTION_CONTACTS

log = logging.getLogger(__name__)

re_dwc_field_label = re.compile('([A-Z]+)')

re_url_validation = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:['
    r'A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)

AUTHOR_MAX_LENGTH = 100


def get_site_statistics():
    """
    Get statistics for the site.
    """
    stats = dict()
    stats['dataset_count'] = get_dataset_count()
    stats['contributor_count'] = get_contributor_count()
    stats['record_count'] = get_record_count()
    return stats


@cache_region('collection_stats', 'contributor_count')
def get_contributor_count():
    """
    Get the total number of authors listed on packages, calculated using Solr facets.
    """
    query = toolkit.get_action('package_search')(
        {}, {'facet.field': ['author'], 'facet.limit': -1}
    )
    return len(query.get('facets', {}).get('author', {}).keys())


@cache_region('collection_stats', 'dataset_count')
def get_dataset_count():
    return toolkit.get_action('package_search')({}, {'rows': 1})['count']


@cache_region('collection_stats', 'record_count')
def get_record_count():
    """
    Get the current total number of records in the collections dataset.
    """
    record_count = 0
    try:
        dataset_statistics = _get_action('dataset_statistics', {})
        record_count = dataset_statistics.get('total', 0)
    except Exception as _e:
        # if there was a problem getting the stats return 0 and log an exception
        log.exception('Could not gather dataset statistics')
    return record_count


@cache_region('collection_stats', 'record_stats')
def get_record_stats():
    start_version = 1501545600
    end_version = int(time.time())
    count_action = toolkit.get_action('datastore_count')

    record_stats = []

    for v in range(start_version, end_version, 604800):
        record_stats.append(
            {
                'date': datetime.fromtimestamp(v),
                'count': count_action({}, {'version': v * 1000}),
            }
        )

    return record_stats


def _get_action(action, params):
    """
    Call basic get_action from template.

    :param action:
    :param params:
    """
    context = {'ignore_auth': True, 'for_view': True}

    try:
        return toolkit.get_action(action)(context, params)
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        pass

    return None


def get_package(package_id):
    """
    Get data for the given package.

    :param package_id: the ID of the package
    """
    return _get_action('package_show', {'id': package_id})


def get_resource(resource_id):
    """
    Get data for the given resource.

    :param resource_id: the ID of the resource
    """
    return _get_action('resource_show', {'id': resource_id})


def get_record(resource_id, record_id):
    """
    Get data for the given record.

    :param resource_id: the ID of the resource holding the record
    :param record_id: the ID of the record
    """
    record = _get_action(
        'record_show', {'resource_id': resource_id, 'record_id': record_id}
    )
    return record.get('data', None)


def form_select_update_frequency_options():
    """
    Get update frequencies as a form list.
    """
    return list_to_form_options(UPDATE_FREQUENCIES)


def update_frequency_get_label(value):
    """
    Get the label for this update frequency.

    :param value: return:
    """
    for v, label in UPDATE_FREQUENCIES:
        if v == value:
            return label


def dataset_categories():
    """
    Return list of dataset category terms.

    :returns: list
    """
    try:
        return toolkit.get_action('tag_list')(
            data_dict={'vocabulary_id': DATASET_TYPE_VOCABULARY}
        )
    except toolkit.ObjectNotFound:
        return []


def url_for_collection_view(view_type=None, filters={}):
    """
    Return URL to link through to specimen dataset view, with optional search params.

    :param view_type: grid to link to - grid or map (optional, default: None)
    :param kwargs: search filter params
    :param filters:  (optional, default: {})
    :returns: url
    """
    resource_id = get_specimen_resource_id()
    return url_for_resource_view(resource_id, view_type, filters)


def url_for_indexlot_view():
    """
    Return URL to link through to index lot resource view.

    :returns: url
    """
    resource_id = get_indexlot_resource_id()
    return url_for_resource_view(resource_id)


def url_for_resource_view(resource_id, view_type=None, filters={}):
    """
    Get URL to link to resource view. If no view type is specified, the first view will
    be used.

    :param resource_id:
    :param filters: (optional, default: {})
    :param view_type:  (optional, default: None)
    """

    try:
        views = toolkit.get_action('resource_view_list')({}, {'id': resource_id})
    except toolkit.ObjectNotFound:
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

        filters = '|'.join([f'{k}:{v}' for k, v in filters.items()])

        return toolkit.url_for(
            'resource.read',
            id=view['package_id'],
            resource_id=view['resource_id'],
            view_id=view['id'],
            filters=filters,
        )


@cache_region('collection_stats', 'collection_stats')
def indexlot_count():
    """
    Get the total number of index lots.
    """
    resource_id = get_indexlot_resource_id()

    if not resource_id:
        log.error('Please configure index lot resource ID')

    context = {'user': toolkit.c.user}

    search_params = dict(
        resource_id=resource_id,
        limit=1,
    )
    search = toolkit.get_action('datastore_search')(context, search_params)
    return delimit_number(search.get('total', 0))


def get_nhm_organisation_id():
    """
    Get the organisation ID for the NHM.

    :returns: ID for the NHM organisation
    """
    value = toolkit.config.get('ldap.organization.id')
    return str(value) if value is not None else None


def is_collection_resource_id(resource_id: str) -> bool:
    """
    Given a resource ID, returns True if the resource ID is one of the designated
    collection IDs.

    :param resource_id: the resource ID
    :return: True if the resource ID is one of the collection resource IDs, False if not
    """
    resource_ids = {
        get_artefact_resource_id(),
        get_indexlot_resource_id(),
        get_specimen_resource_id(),
    }
    return resource_id in resource_ids


def get_specimen_resource_id():
    """
    Get the ID for the specimens dataset.

    :returns: ID for the specimen resource
    """
    value = toolkit.config.get('ckanext.nhm.specimen_resource_id')
    return str(value) if value is not None else None


def get_indexlot_resource_id():
    """
    Get the ID for the index lots dataset.

    :returns: ID for indexlot resource
    """
    value = toolkit.config.get('ckanext.nhm.indexlot_resource_id')
    return str(value) if value is not None else None


def get_artefact_resource_id():
    '''
    @return:  ID for artefact resource
    '''
    return toolkit.config.get('ckanext.nhm.artefact_resource_id')


def get_beetle_iiif_resource_id():
    """
    Get the ID for the beetle IIIF resource.

    :return: the resource id
    """
    value = toolkit.config.get('ckanext.nhm.beetle_iiif_resource_id')
    return str(value) if value is not None else None


@cache_region('collection_stats', 'collection_stats')
def collection_stats():
    """
    Get collection stats, including collection codes and collection totals.
    """
    stats = {}
    collections = [
        ('artefacts', get_artefact_resource_id()),
        ('indexlots', get_indexlot_resource_id()),
        ('specimens', get_specimen_resource_id()),
    ]

    collections_total = 0
    for name, resource_id in collections:
        params = {
            'resource_id': resource_id,
            'limit': 0,
        }
        stats[name] = toolkit.get_action('datastore_search')({}, params)['total']
        collections_total += stats[name]
    stats['total'] = collections_total

    collection_code_counts = []
    for collection_code in ('PAL', 'MIN', 'BMNH(E)', 'ZOO', 'BOT'):
        params = {
            'resource_id': get_specimen_resource_id(),
            'limit': 0,
            'query': {
                'filters': {
                    'and': [
                        {
                            'string_equals': {
                                'fields': ['collectionCode'],
                                'value': collection_code,
                            }
                        }
                    ]
                }
            },
        }
        total = toolkit.get_action('datastore_multisearch')({}, params)['total']
        collection_code_counts.append((collection_code, total))

    collection_code_counts.sort(key=operator.itemgetter(1), reverse=True)
    stats['collectionCodes'] = OrderedDict(collection_code_counts)

    return stats


def get_department(collection_code):
    """
    Return a department name for collection code.

    :param collection_code: BOT, PAL etc.,
    :returns: Full department name - Entomology
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
    Separate long number into thousands 1000000 => 1,000,000.

    :param num:
    """
    return '{:,}'.format(num)


def api_doc_link():
    """
    Link to API documentation.
    """
    attr = {'class': 'external', 'target': '_blank'}
    return toolkit.h.link_to(
        toolkit._('API guide'), 'http://docs.ckan.org/en/latest/api/index.html', **attr
    )


def persistent_follow_button(obj_type, obj_id):
    """
    Replaces ckan.lib.follow_button which returns an empty string for anonymous users.
    For anon users this function outputs a follow button which links through to the
    login page.

    :param obj_type:
    :param obj_id:
    :returns:
    """
    obj_type = obj_type.lower()
    assert obj_type in toolkit.h._follow_objects

    if toolkit.c.user:
        context = {'user': toolkit.c.user}
        action = f'am_following_{obj_type}'
        following = toolkit.get_action(action)(context, {'id': obj_id})
        return toolkit.h.snippet(
            'snippets/follow_button.html',
            following=following,
            obj_id=obj_id,
            obj_type=obj_type,
        )

    return toolkit.h.snippet(
        'snippets/anon_follow_button.html', obj_id=obj_id, obj_type=obj_type
    )


def filter_and_format_resource_items(resource):
    """
    Given a resource, return the items from it that are whitelisted for display and
    format them.

    :param resource: the resource dict
    :return: a list of made up of 2-tuples containing formatted keys and values from
    the resource
    """
    blacklist = {
        '_image_field',
        '_title_field',
        '_subtitle_field',
        'datastore_active',
        'has_views',
        'on_same_domain',
        'resource_group_id',
        'revision_id',
        'url_type',
    }
    items = []
    for key, value in resource.items():
        if key not in blacklist:
            items.append((key, value))
    return toolkit.h.format_resource_items(items)


def get_map_styles():
    """
    New map config overriding the marker point img.
    """
    return {
        'point': {
            'iconUrl': '/images/leaflet/marker-icon.png',
            'iconSize': [20, 34],
            'iconAnchor': [12, 30],
        }
    }


def get_query_params():
    """
    Helper function to build a dict of query params To be used in urls for persistent
    filters.

    :returns: dict
    """
    params = dict()

    for key in ['q', 'filters']:
        value = toolkit.request.params.get(key)
        if value:
            params[key] = value

    return params


def resource_view_get_field_groups(resource):
    """
    Return dictionary of field groups.

    :param resource: resource dict
    :returns: OrderedDict of fields
    """
    view_cls = resource_view_get_view(resource)

    return view_cls.get_field_groups(resource)


def get_resource_fields(resource, version=None, use_request_version=False):
    """
    Retrieves the fields for the given resource. This is done using the datastore_search
    action. By default, the field names from the latest version of the resource are
    returned. However, this can be altered by either passing a version (must be an
    integer) or by having a version filter in the request and then passing
    use_request_version=True. The version is extracted from the __version__ filter as
    defined by the versioned-datastore plugin. If we can start passing the version as a
    parameter in its own right rather than as part of the filters then we can change
    this code.

    If the resource isn't a datastore resource then an empty list is returned.

    Because the versioned_datastore plugin guarantees that the fields returned in its
    datastore_search responses will be in the order they were when they were ingested or sorted
    alphabetically if no ingestion ordering is available, no field sorting occurs in this function.

    :param resource: the resource dict
    :param version: the version to request (default: None)
    :param use_request_version: whether to look in the request parameters to find a version in the
                                filters (default: False)
    :return: a list of field names
    """
    if not resource.get('datastore_active'):
        return []

    data = {'resource_id': resource['id'], 'limit': 0}

    if version is not None:
        data['version'] = version
    elif use_request_version:
        filters = parse_request_filters()
        if '__version__' in filters:
            data['version'] = int(filters['__version__'][0])

    result = toolkit.get_action('datastore_search')({}, data)
    return [field['id'] for field in result.get('fields', [])]


# Resource view and filters
def resource_view_state(resource_view_json, resource_json):
    """
    Alter the recline view resource, adding in state info.

    :param resource_view_json: return:
    :param resource_json:
    """
    resource_view = json.loads(resource_view_json)
    resource = json.loads(resource_json)

    fields = get_resource_fields(resource, use_request_version=True)

    # Initiate the resource view
    view = resource_view_get_view(resource)
    # And get the state
    resource_view['state'] = view.get_slickgrid_state()

    # there is an annoying feature/bug in slickgrid that if fitColumns=True and grid is wider than
    # available viewport, slickgrid columns cannot be resized until fitColumns is deactivated. So to
    # fix, we're going to work out how many columns are in the dataset to decide whether or not to
    # turn on fitColumns. Messy, but better than trying to hack around with slickgrid
    viewport_max_width = 920
    col_width = 100
    fit_columns = (len(fields) * col_width) < viewport_max_width
    # TODO: This can be merged into get_slickgrid_state
    resource_view['state']['fitColumns'] = fit_columns

    # ID and DQI always first
    columns_order = ['_id']
    if 'gbifIssue' in fields:
        columns_order.append('gbifIssue')
    # add other useful DwC fields
    if 'currentScientificName' in fields:
        # prefer current scientific name
        columns_order.append('currentScientificName')
    elif 'scientificName' in fields:
        columns_order.append('scientificName')
    for f in [
        'typeStatus',
        'type',
        'phylum',
        'class',
        'order',
        'family',
        'genus',
        'specificEpithet',
        'infraspecificEpithet',
        'locality',
        'country',
        'recordedBy',
        'catalogNumber',
        'associatedMedia',
        'preservative',
        'collectionCode',
        'year',
        'month',
        'day',
    ]:
        if f in fields:
            columns_order.append(f)
    # Add the rest of the columns to the columns order
    columns_order += [f for f in fields if f not in columns_order]
    resource_view['state']['columnsOrder'] = list(columns_order)

    # this is a bit of a hack but not the worst thing that's ever happened. This code is here to
    # solve a specific problem whereby if a user is viewing an old version of the data and in newer
    # versions of the data new columns have been added, the user will see these new columns in the
    # slick grid header row (no data will be shown for them because the column doesn't exist in the
    # old records). This happens because when slick is setting up it requests the data and the
    # column headers in separate datastore_search requests, this is inefficient but also problematic
    # because the column headers request doesn't include any of the filters or query parameters that
    # the data request does. This means that we lose the version information and will return the
    # headers in the latest version even if the user is actually looking at older data. By
    # retrieving the current fields for the resource here and then using this list to generate a
    # list of hidden columns to pass to slick we can make sure these columns don't appear. If we
    # stop using slick or slick is fixed we can stop doing this.
    latest_fields = get_resource_fields(resource, use_request_version=False)
    resource_view['state']['hiddenColumns'] = [
        f for f in latest_fields if f not in fields
    ]

    if view.grid_column_widths:
        for column, width in view.grid_column_widths.items():
            resource_view['state']['columnsWidth'].append(
                {'column': column, 'width': width}
            )

    try:
        return json.dumps(resource_view)
    except TypeError:
        return {}


def resource_is_dwc(resource):
    """
    Is the resource format DwC?

    :param resource: return:
    """
    return bool(resource.get('format').lower() == 'dwc')


def camel_case_to_string(camel_case_string):
    '''

    :param camel_case_string:

    '''
    s = ' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', camel_case_string))
    return s[0].upper() + s[1:]


def get_resource_filter_options(resource, resource_view):
    """
    Return the available filter options for the given resource.

    :param resource: Dictionary representing a resource
    :param resource_view:
    :returns: A dictionary associating each option's name to a dict defining:
                - label: The label to display to users;
                - checked: True if the option is currently applied.
    """
    options = resource_view_get_filter_options(resource)
    filter_list = toolkit.request.params.get('filters', '').split('|')
    filters = {}

    # If this is a gallery view, hide the has image filter
    # Only records with images will be displayed anyway
    # if resource_view['view_type'] == 'gallery':
    #     options.pop('_has_image', None)

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
        result[option.name]['checked'] = (
            option.name in filters and 'true' in filters[option.name]
        )
    return result


def get_resource_gbif_errors(resource):
    """
    Return GBIF errors applicable for this resource i.e. if this the specimen resource,
    return the gbif errors dict.

    :param resource: return:
    """

    # If this is a
    if resource.get('id') == get_specimen_resource_id():
        return GBIF_ERRORS
    else:
        return {}


def get_allowed_view_types(resource, package):
    """
    Overwrite ckan.lib.helpers.get_allowed_view_types.

    We want to edit some of the options - remove Image and change Tiled Map to Map

    :param resource: param package:
    :param package:
    """

    view_types = core_helpers.get_allowed_view_types(resource, package)
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
    """
    For a given facet, return the function used to fetch the facet's items labels.

    :param facet_name: Facet name
    :param multi: If True, the function returned should take a list of facets and a
                  filter value to find the matching facet on the name field (optional,
                  default: False)
    :returns: A function or None
    """
    facet_function = None
    if facet_name == 'creator_user_id':
        facet_function = get_creator_id_facet_label

    if facet_function and multi:

        def filter_facets(facet, filter_value):
            '''

            :param facet:
            :param filter_value:

            '''
            for f in facet:
                if f['name'] == filter_value:
                    return facet_function(f)
            return filter

        return filter_facets
    else:
        return facet_function


def get_creator_id_facet_label(facet):
    """
    Return display name for the creator_id facet.

    :param facet: A dictionary representing a single value for the facet
    :returns: A string to use for display name
    """
    try:
        user = model.User.get(facet['name'])
        display_name = user.display_name
    except (toolkit.ObjectNotFound, AttributeError) as e:
        display_name = facet['display_name']
    return display_name


def field_name_label(field_name):
    '''Convert a field name into a label - replacing _s and upper casing first character

    :param field_name:
    :returns: str label

    '''
    label = field_name.replace('_', ' ')
    label = label[0].upper() + label[1:]
    return label


def field_is_link(value):
    """
    Is a field a link (starts with http and is a valid URL)

    :param value:
    :returns: boolean
    """
    try:
        return value.startswith('http') and re_url_validation.match(value)
    except Exception:
        pass
    return False


def get_contact_form_department_options():
    """
    Contact form category.
    """
    return list_to_form_options(
        COLLECTION_CONTACTS.keys(),
        allow_empty=True,
        allow_empty_text='Select an option',
    )


def downloadable(resource):
    """
    Is a resource downloadable.

    :param resource: return: bool
    :returns: bool
    """
    return bool(resource['format']) or resource.get('datastore_active', False)


def is_sysadmin():
    """
    Is user a sysadmin user.
    """
    if toolkit.c.userobj.sysadmin:
        return True


def record_display_field(field_name, value):
    """
    Decide whether to display a field Evaluates whether a field has value.

    :param field_name:
    :param value:
    :returns: bool - true to display field; false not to
    """

    # If this is a string, strip it before evaluating
    if isinstance(value, str):
        value = value.strip()

    return bool(value)


def group_fields_have_data(record_dict, fields):
    """
    Are any of the fields in the group populated Return true if they are; false if not.

    :param record_dict: record data
    :param fields: fields to test
    :returns: bool
    """

    for field in fields:
        if record_dict.get(field, None):
            return True


def get_image_licence_options():
    """
    Return list of image licences Currently this is the same list as dataset licences.
    """

    licenses = [('', '')] + model.Package.get_license_options()

    # Format licences as form options list of dicts
    return [{'value': value, 'text': text} for text, value in licenses]


def social_share_text(pkg_dict=None, res_dict=None, rec_dict=None):
    """
    Generate social share text for a package.

    @param pkg_dict:
    @return:
    """
    text = []
    if rec_dict:
        title_field = res_dict.get('_title_field', None)
        if title_field and rec_dict.get(title_field, None):
            text.append(rec_dict[title_field])
        else:
            text.append('Record {}'.format(rec_dict['_id']))
    elif res_dict:
        text.append(res_dict['name'])
    elif pkg_dict:
        text.append(pkg_dict['title'] or pkg_dict['name'])

    text.append('on the @NHM_London Data Portal')

    try:
        text.append(f'DOI: {"/".join(["https://doi.org", pkg_dict["doi"]])}')
    except KeyError:
        pass

    return quote(' '.join(map(str, text)).encode('utf8'))


def accessible_gravatar(email_hash, size=100, default=None, userobj=None):
    """
    Port of ckan helper gravatar Adds title text to the image so it passes accessibility
    checks.

    :param email_hash:
    :param default: (optional, default: None)
    :param size:  (optional, default: 100)
    :param userobj:  (optional, default: None)
    """
    gravatar_literal = toolkit.h.gravatar(email_hash, size, default)
    if userobj is not None:
        grav_xml = etree.fromstring(gravatar_literal)
        grav_xml.attrib['alt'] = userobj.name
        gravatar_literal = literal(etree.tostring(grav_xml, encoding='unicode'))

    return gravatar_literal


def dataset_author_truncate(author_str):
    """
    For author strings with lots of authors need to shorten for display insert et al as
    abbreviation tag.

    :param author_str: dataset author
    :returns: shortened author str, full text in abbr tag
    """

    def _truncate(author_str, separator=None):
        '''

        :param author_str:
        :param separator:  (optional, default: None)

        '''

        # If we have a separator, split string on it
        if separator:
            shortened = ';'.join(author_str.split(separator)[0:4])
        else:
            # Otherwise use the jinja truncate function (may split author name)
            shortened = do_truncate(author_str, length=AUTHOR_MAX_LENGTH, end='')

        return literal(
            '{0} <abbr title="{1}" style="cursor: pointer;">et al.</abbr>'.format(
                shortened, author_str
            )
        )

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
    Return a list of facets for a particular resource.

    :param resource:
    """
    # Number of facets to display
    num_facets = 10
    resource_view = resource_view_get_view(resource)
    # if facets aren't defined in the resource view, then just return
    if not resource_view.field_facets:
        return
    context = {'user': toolkit.c.user}
    # Build query parameters for the faceted search
    # We'll use the same query parameters used in the current request
    # And then add extras to perform a solr faceted query, returning
    # facets but zero results (limit=0)
    query_params = get_query_params()

    # Convert filters to a dictionary as this won't happen automatically
    # as we're retrieving raw get parameters from get_query_params
    filters = defaultdict(list)
    if query_params.get('filters'):
        for f in query_params.get('filters').split('|'):
            filter_field, filter_value = f.split(':', 1)
            filters[filter_field].append(filter_value)

    search_params = dict(
        resource_id=resource.get('id'),
        # use limit 0 as we're not interested in getting any results, just the facets
        limit=0,
        facets=resource_view.field_facets,
        q=query_params.get('q', None),
        filters=filters,
    )

    # if the show more button is clicked, a parameter is added to the query which
    # informs us we need
    # to show more facets, so use 50 for the facet limit on the given field
    for field_name in resource_view.field_facets:
        if toolkit.h.get_param_int('_{}_limit'.format(field_name)) == 0:
            search_params.setdefault('facet_limits', {})[field_name] = 50

    search = toolkit.get_action('datastore_search')(context, search_params)
    facets = []

    # dictionary of facet name => formatter function with camel_case_to_string defined
    # as the
    # default formatting function and then any overrides for specific edge cases
    facet_label_formatters = defaultdict(
        lambda: camel_case_to_string,
        **{
            # specific lambda for GBIF to ensure it's capitalised correctly
            'gbifIssue': lambda _: 'GBIF Issue'
        },
    )

    # Dictionary of field name => formatter function
    # Pass facet value to a formatter to get a better facet item label, if the facet
    # doesn't have a
    # formatter defined then the value is just used as is
    facet_field_label_formatters = defaultdict(
        lambda: (lambda v: v.capitalize()), **{'collectionCode': get_department}
    )

    # Loop through original facets to ensure order is preserved
    for field_name in resource_view.field_facets:
        # parse the facets into a list of dictionary values
        facets.append(
            {
                'name': field_name,
                'label': facet_label_formatters[field_name](field_name),
                'active': field_name in filters,
                'has_more': search['facets'][field_name]['details'][
                    'sum_other_doc_count'
                ]
                > 0,
                'facet_values': [
                    {
                        'name': value,
                        'label': facet_field_label_formatters[field_name](value),
                        'count': count,
                        'active': field_name in filters
                        and value in filters[field_name],
                        # loop over the top values, sorted by count desc so that the top
                        # value is first
                    }
                    for value, count in sorted(
                        search['facets'][field_name]['values'].items(),
                        key=itemgetter(1),
                        reverse=True,
                    )
                ],
            }
        )

    return facets


def remove_url_filter(field, value, extras=None):
    """
    The CKAN built in functions remove_url_param / add_url_param cannot handle multiple
    filters which are concatenated with |, not separate query params This replaces
    remove_url_param for filters.

    :param field: the field to remove the filter for
    :param value: the value of the field to remove the filter for
    :param extras: extra parameters to include in the created URL
    :return: a URL
    """

    params = dict(toolkit.request.params)
    try:
        del params['filters']
    except KeyError:
        pass
    else:
        filters = parse_request_filters()
        if field in filters:
            # Convert all filters to unicode for ease of comparison
            filters[field] = [f.lower() for f in filters[field]]
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
                filter_parts.append(f'{filter_field}:{filter_value}')
        # If we have filter parts, add them back to the params dict
        if filter_parts:
            filters = '|'.join(filter_parts)
            return toolkit.h.remove_url_param('filters', replace=filters, extras=extras)
    return toolkit.h.remove_url_param('filters', extras=extras)


def add_url_filter(field, value, extras=None):
    """
    The CKAN built in functions remove_url_param / add_url_param cannot handle multiple
    filters which are concatenated with |, not separate query params This replaces
    add_url_param for filters.

    :param field:
    :param extras:
    :param value:
    """

    params = {k: v for k, v in toolkit.request.params.items() if k != 'page'}
    url_filter = f'{field}:{value}'
    filters = [
        f for f in params.get('filters', '').split('|') + [url_filter] if f != ''
    ]
    filters = '|'.join(filters)
    params['filters'] = filters
    return core_helpers._url_with_params(toolkit.request.base_url, params.items())


def parse_request_filters():
    """
    Get the filters from the request object.
    """
    filter_dict = {}

    try:
        filter_params = toolkit.request.params.get('filters').split('|')
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
    Get filter pills.

    We don't want the field group pills - these are handled separately in
    get_resource_field_groups

    :param resource: param package:
    :param package:
    :param resource_view:  (optional, default: None)
    """

    if not isinstance(package, dict):
        package = package.as_dict()

    filter_dict = parse_request_filters()
    extras = {'id': package['id'], 'resource_id': resource['id']}

    # there are some special filter field names provided by versioned-datastore which
    # should have
    # their values formatted differently to normal filter values
    special = {
        # display a human readable timestamp
        '__version__': lambda value: [
            time.strftime('%Y/%m/%d, %H:%M:%S', time.localtime(int(v) / 1000))
            for v in value
        ],
        # display the type of the GeoJSON filter
        '__geo__': lambda value: [json.loads(v)['type'] for v in filter_value],
    }

    pills = []

    for filter_field, filter_value in filter_dict.items():
        # if the field name stars with an underscore, don't include it in the pills (
        # unless it's
        # special!)
        if filter_field.startswith('_') and filter_field not in special:
            continue

        # remove filter from url function
        href = remove_url_filter(filter_field, filter_value, extras=extras)

        pills.append(
            {
                'label': camel_case_to_string(filter_field),
                'field': filter_field,
                # if the filter isn't a special one, just use the value
                'value': ' '.join(
                    special.get(filter_field, lambda value: value)(filter_value)
                ),
                'href': href,
            }
        )

    return pills


def resource_view_get_filterable_fields(resource):
    """
    Retrieves the fields that can be filtered on.

    @return: a list of sorted fields
    """
    # if this isn't a datastore resource, return an empty list
    if not resource.get('datastore_active'):
        return []

    # otherwise, query the datastore for the fields
    data = {
        'resource_id': resource['id'],
        'limit': 0,
    }
    fields = toolkit.get_action('datastore_search')({}, data).get('fields', [])

    # sort and filter the fields ensuring we only return string type fields and don't
    # return the id
    # field
    return sorted(f['id'] for f in fields if f['type'] == 'string' and f['id'] != '_id')


def form_select_datastore_field_options(resource, allow_empty=True):
    '''

    :param resource:
    :param allow_empty:  (optional, default: True)

    '''
    fields = toolkit.h.resource_view_get_fields(resource)
    return list_to_form_options(fields, allow_empty)


def _get_latest_update(package_or_resource_dicts):
    """
    Given a sequence of package and/or resource dicts, returns the most recent update
    datetime available from them, or None if there is no update datetime found.

    :param package_or_resource_dicts: a sequence of the package or resource dicts
    :return: a 2-tuple containing the latest datetime and the dict from which it came,
    if no times
             are found then (None, None) is returned
    """
    # a list of fields on the resource that should contain update dates
    fields = ['last_modified', 'revision_timestamp', 'Created']
    get_rounded_version = toolkit.get_action('datastore_get_rounded_version')

    latest_dict = None
    latest_date = None
    for package_or_resource_dict in package_or_resource_dicts:
        dates = [package_or_resource_dict.get(field, None) for field in fields]

        # check if this is a datastore resource
        if package_or_resource_dict.get('datastore_active', False):
            pkg_version = get_rounded_version(
                {}, {'resource_id': package_or_resource_dict['id']}
            )
            # could be a datastore resource with no records, ignore if so
            if pkg_version is None:
                continue
            version_date = datetime.fromtimestamp(pkg_version / 1000)
            dates.append(version_date)

        for datestamp in dates:
            date = core_helpers._datestamp_to_datetime(datestamp)
            if date is not None and (latest_date is None or date > latest_date):
                latest_date = date
                latest_dict = package_or_resource_dict

    return latest_date, latest_dict


def get_latest_update_for_package(pkg_dict, date_format=None):
    """
    Returns the most recent update datetime (formatted as a string) for the package and
    its resources. If there is no update time found then 'unknown' is returned. If there
    is datetime found then it is rendered using the standard ckan helper.

    :param pkg_dict:        the package dict
    :param date_format:     date format for the return datetime
    :return: 'unknown' or a string containing the rendered datetime
    """
    latest_date, _ = _get_latest_update(
        itertools.chain([pkg_dict], pkg_dict.get('resources', []))
    )
    if latest_date is not None:
        return toolkit.h.render_datetime(latest_date, date_format=date_format)
    else:
        return toolkit._('unknown')


def get_latest_update_for_package_resources(pkg_dict, date_format=None):
    """
    Returns the most recent update datetime (formatted as a string) across all resources
    in this package. If there is no update time found then 'unknown' is returned. If
    there is datetime found then it is rendered using the standard ckan helper.

    :param pkg_dict:        the package dict
    :param date_format:     date format for the return datetime
    :return: 'unknown' or a string containing the rendered datetime and the resource name
    """
    latest_date, latest_resource = _get_latest_update(pkg_dict.get('resources', []))
    if latest_date is not None:
        name = latest_resource['name']
        return f'{toolkit.h.render_datetime(latest_date, date_format=date_format)} ({name})'
    # there is no available update so we return 'unknown'
    return toolkit._('unknown')


def get_external_sites(record: dict) -> List[Site]:
    """
    Helper called on collection record pages (i.e. records in the specimens, indexlots
    or artefacts resources) which is expected to return a list of Site objects. From
    these sites, links can be generated which are relevant to the record.

    :param record: a record dict
    :return: a list of Site objects
    """
    return external_links.get_sites(record)


def render_epoch(
    epoch_timestamp, in_milliseconds=True, date_format='%Y-%m-%d %H:%M:%S (UTC)'
):
    """
    Renders an epoch timestamp in the given date format. The timestamp is rendered in
    UTC.

    :param epoch_timestamp: the timestamp, represented as the number of seconds (or
    milliseconds if
                            in_milliseconds is True) since the UNIX epoch
    :param in_milliseconds: whether the timestamp is in milliseconds or seconds. By
    default this is
                            True and therefore the timestamp is expected to be in
                            milliseconds
    :param date_format: the output format. This will be passed straight to datetime's
    strftime
                        function and therefore uses its keywords etc. Defaults to:
                        %Y-%m-%d %H:%M:%S (UTC)
    :return: a string rendering of the timestamp using the
    """
    if in_milliseconds:
        epoch_timestamp = epoch_timestamp / 1000
    return datetime.utcfromtimestamp(epoch_timestamp).strftime(date_format)


def get_object_url(resource_id, guid, version=None, include_version=True):
    """
    Retrieves the object url for the given guid in the given resource with the given
    version. If the version is None then the latest version of the resource is used.

    The version passed (if one is passed) is not used verbatim, a call to the versioned search
    extension is put in to retrieve the rounded version of the resource so that the object url we
    create is always correct.

    :param resource_id: the resource id
    :param guid: the guid of the object
    :param version: the version (default: None which means use the latest version)
    :param include_version: whether to include the version in the object URL or not. If this is
                            False the version parameter is ignored (default: True)
    :return: the object url
    """
    if include_version:
        rounded_version = toolkit.get_action('datastore_get_rounded_version')(
            {},
            {
                'resource_id': resource_id,
                'version': version,
            },
        )
    else:
        rounded_version = None
    return toolkit.url_for(
        'object.view', uuid=guid, qualified=True, version=rounded_version
    )


def build_specimen_nav_items(package_name, resource_id, record_id, version=None):
    """
    Creates the specimen nav items allowing the user to navigate to different views of
    the specimen record data. A list of nav items is returned.

    :param package_name: the package name (or id)
    :param resource_id: the resource id
    :param record_id: the record id
    :param version: the version of the record, or None if no version is present
    :return: a list of nav items
    """
    link_definitions = [
        ('record.view', toolkit._('Normal view')),
        ('record.dwc', toolkit._('Darwin Core view')),
    ]
    links = []
    for route_name, link_text in link_definitions:
        nav_item = toolkit.h.build_nav_icon(
            route_name,
            link_text,
            package_name=package_name,
            resource_id=resource_id,
            record_id=record_id,
            version=version,
        )
        links.append(_add_nav_item_class(nav_item, classes=[], role='presentation'))

    return links


def _add_nav_item_class(html_string, classes=None, **kwargs):
    """
    Add classes to list items in an HTML string.

    :param html_string: a literal or string of HTML code
    :param classes: CSS classes to add to each item
    :param kwargs: other attributes to add to each item
    :return: a literal of HTML code where all the <li> nodes have "nav-item" added to their classes
    """
    if classes is None:
        classes = ['nav-item']
    tree = html.fromstring(html_string)
    list_items = [i for i in tree.getchildren() if i.tag == 'li']
    for li in list_items:
        for c in classes:
            li.classes.add(c)
        for k, v in kwargs.items():
            li.attrib[k] = v
    return literal(
        '\n'.join(html.tostring(el, encoding='unicode') for el in tree.getchildren())
    )


def build_nav_main(*args):
    """
    Build a set of menu items. Overrides core CKAN method to add "nav-item" class to li
    elements.

    :param args: tuples of (menu type, title) eg ('login', _('Login'))
    :return: literal - <li class="nav-item"><a href="...">title</a></li>
    """
    from_core = core_helpers.build_nav_main(*args)
    return _add_nav_item_class(from_core)


def get_specimen_jsonld(uuid, version=None):
    """
    Returns the rdf representation of the given specimen uuid. The returned data is a
    string of json-ld data. If something goes wrong, an empty string is returned.

    :param uuid: the uuid of the specimen record
    :param version: optional version for the record data
    :return: string of dumped json-ld data
    """
    data_dict = {
        'uuid': uuid,
        'format': 'json-ld',
        'version': version,
    }
    try:
        return toolkit.get_action('object_rdf')({}, data_dict)
    except toolkit.ValidationError:
        return ''


def get_resource_group(resource):
    group_name = resource.get('resource_group')
    linked_specimen = resource.get('linked_specimen')
    if linked_specimen and group_name and '$' in group_name:
        # has to be imported here due to circular imports
        from ckanext.nhm.lib.record import get_specimen_by_uuid

        linked_specimen_record = get_specimen_by_uuid(linked_specimen)
        if linked_specimen_record and group_name:
            tokens = [
                t
                for t in re.findall('\$[a-zA-Z]+', group_name)
                if t.strip('$') in linked_specimen_record.data
            ]
            for token in tokens:
                group_name = group_name.replace(
                    token, linked_specimen_record.data.get(token.strip('$'))
                )
    if (group_name or '').strip() == '':
        group_name = None
    return group_name


def group_resources(resource_list):
    group_and_resource = sorted(
        [(get_resource_group(r), r) for r in resource_list], key=lambda x: x[0] or ''
    )
    return [
        (
            group_name,
            re.sub('[^A-Za-z0-9]', '', group_name or 'ungrouped'),
            [x[1] for x in resources],
        )
        for group_name, resources in itertools.groupby(
            group_and_resource, key=itemgetter(0)
        )
    ]


def get_resource_size(resource_dict):
    prefixes = 'KMGTPEZ'  # kilo, mega, giga, etc. I could make this a list but what's the point
    if toolkit.get_action('datastore_is_datastore_resource')(
        {}, {'resource_id': resource_dict['id']}
    ):
        try:
            records = toolkit.get_action('datastore_count')(
                {}, {'resource_ids': [resource_dict['id']]}
            )
            return f'{records} records'
        except:
            return 'Unknown size'
    sz = resource_dict.get('Size')
    if sz is None:
        return 'Unknown size'
    p = ''
    while sz >= 1024:
        p = prefixes[0]
        prefixes = prefixes[1:]
        sz /= 1024
    return f'{round(sz)}{p}B'


def get_record_permalink(
    resource_dict, record_dict, version=None, include_version=False
):
    try:
        url = get_object_url(
            resource_dict['id'], record_dict['occurrenceID'], version, include_version
        )
    except KeyError:
        url_for_params = {
            'resource_id': resource_dict['id'],
            'record_id': record_dict['_id'],
        }
        if include_version:
            rounded_version = toolkit.get_action('datastore_get_rounded_version')(
                {},
                {
                    'resource_id': resource_dict['id'],
                    'version': version,
                },
            )
            url_for_params['version'] = rounded_version
        url = toolkit.url_for('record.permalink', qualified=True, **url_for_params)
    return url


def get_record_iiif_manifest_url(resource_id: str, record_id: int) -> str:
    """
    Given a resource ID and a record ID, a fully qualified URL to the IIIF manifest for
    the record's images.

    :param resource_id: the resource ID
    :param record_id: the record ID
    :return: the fully qualified URL
    """
    manifest_id = toolkit.get_action('build_iiif_identifier')(
        {},
        {'builder_id': 'record', 'resource_id': resource_id, 'record_id': record_id},
    )
    return toolkit.url_for('iiif.resource', identifier=manifest_id, _external=True)


def get_status_indicator():
    """
    Check if we need to display a status indicator, and if so what type.

    :return: 'red', 'amber', or None (if no alerts)
    """
    # is there a status message?
    status_message = toolkit.config.get('ckanext.status.message', None)
    if status_message:
        return 'red'

    try:
        status_reports = toolkit.get_action('status_list')({}, {}).get('reports', [])
    except KeyError:
        # if the action doesn't exist
        status_reports = []

    # are there any 'bad' items?
    red_status = [r for r in status_reports if r['state'] == 'bad']
    if len(red_status) > 0:
        return 'red'

    # are there any reports with small issues?
    amber_status = [r for r in status_reports if r['state'] == 'ok']
    if len(amber_status) > 0:
        return 'amber'
