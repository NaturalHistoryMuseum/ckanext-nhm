#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import json
import logging
import urllib
from collections import OrderedDict, defaultdict
from operator import itemgetter

import os
import re
from beaker.cache import cache_region
from ckanext.gbif.lib.errors import GBIF_ERRORS
from ckanext.nhm.lib import external_links
from ckanext.nhm.lib.form import list_to_form_options
from ckanext.nhm.lib.resource_view import (resource_view_get_filter_options,
                                           resource_view_get_view)
from ckanext.nhm.lib.taxonomy import extract_ranks
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY, UPDATE_FREQUENCIES
from ckanext.nhm.settings import COLLECTION_CONTACTS
from jinja2.filters import do_truncate
from solr import SolrException
from webhelpers.html import literal

import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger(__name__)

re_dwc_field_label = re.compile(u'([A-Z]+)')

re_url_validation = re.compile(r'^(?:http)s?://'  # http:// or https://
                               r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:['
                               r'A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                               r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                               r'(?::\d+)?'  # optional port
                               r'(?:/?|[/?]\S+)$', re.IGNORECASE)

AUTHOR_MAX_LENGTH = 100


@cache_region(u'permanent', u'collection_stats')
def get_site_statistics():
    '''Get statistics for the site.'''
    stats = dict()
    stats[u'dataset_count'] = toolkit.get_action(u'package_search')({}, {
        u'rows': 1
        })[
        u'count']
    # Get a count of all distinct user IDs
    stats[u'contributor_count'] = get_contributor_count()
    record_count = 0
    try:
        dataset_statistics = _get_action(u'dataset_statistics', {})
        record_count = dataset_statistics.get(u'total', 0)
    except Exception as _e:
        # if there was a problem getting the stats return 0 and log an exception
        log.exception(u'Could not gather dataset statistics')
    stats[u'record_count'] = record_count
    return stats


def get_contributor_count():
    '''Get the total number of contributors to active packages.'''
    return model.Session.execute(
        u"SELECT COUNT(DISTINCT creator_user_id) FROM package WHERE "
        u"state='active'").scalar()


def _get_action(action, params):
    '''Call basic get_action from template.

    :param action:
    :param params: 

    '''
    context = {
        u'ignore_auth': True,
        u'for_view': True
        }

    try:
        return toolkit.get_action(action)(context, params)
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        pass

    return None


def get_package(package_id):
    '''Get data for the given package.

    :param package_id: the ID of the package

    '''
    return _get_action(u'package_show', {
        u'id': package_id
        })


def get_resource(resource_id):
    '''Get data for the given resource.

    :param resource_id: the ID of the resource

    '''
    return _get_action(u'resource_show', {
        u'id': resource_id
        })


def get_record(resource_id, record_id):
    '''Get data for the given record.

    :param resource_id: the ID of the resource holding the record
    :param record_id: the ID of the record

    '''
    record = _get_action(u'record_show',
                         {
                             u'resource_id': resource_id,
                             u'record_id': record_id
                             })
    return record.get(u'data', None)


def form_select_update_frequency_options():
    '''Get update frequencies as a form list'''
    return list_to_form_options(UPDATE_FREQUENCIES)


def update_frequency_get_label(value):
    '''Get the label for this update frequency

    :param value: return:

    '''
    for v, label in UPDATE_FREQUENCIES:
        if v == value:
            return label


def dataset_categories():
    '''Return list of dataset category terms


    :returns: list

    '''
    try:
        return toolkit.get_action(u'tag_list')(
            data_dict={
                u'vocabulary_id': DATASET_TYPE_VOCABULARY
                })
    except toolkit.ObjectNotFound:
        return []


def url_for_collection_view(view_type=None, filters={}):
    '''Return URL to link through to specimen dataset view, with optional search params.

    :param view_type: grid to link to - grid or map (optional, default: None)
    :param kwargs: search filter params
    :param filters:  (optional, default: {})
    :returns: url

    '''
    resource_id = get_specimen_resource_id()
    return url_for_resource_view(resource_id, view_type, filters)


def url_for_indexlot_view():
    '''Return URL to link through to index lot resource view.

    :returns: url

    '''
    resource_id = get_indexlot_resource_id()
    return url_for_resource_view(resource_id)


def url_for_resource_view(resource_id, view_type=None, filters={}):
    '''Get URL to link to resource view. If no view type is specified,
    the first view will be used.

    :param resource_id:
    :param filters: (optional, default: {})
    :param view_type:  (optional, default: None)

    '''
    context = {
        u'user': toolkit.c.user
        }

    try:
        views = toolkit.get_action(u'resource_view_list')(context, {
            u'id': resource_id
            })
    except toolkit.ObjectNotFound:
        return None
    else:
        if not views:
            return None

        if not view_type:
            view = views[0]
        else:
            for view in views:
                if view[u'view_type'] == view_type:
                    break

        filters = u'|'.join([u'%s:%s' % (k, v) for k, v in filters.items()])

        return toolkit.url_for(controller=u'package', action=u'resource_read',
                               id=view[u'package_id'], resource_id=view[u'resource_id'],
                               view_id=view[u'id'], filters=filters)


@cache_region(u'permanent', u'collection_stats')
def indexlot_count():
    '''Get the total number of index lots.'''
    resource_id = get_indexlot_resource_id()

    if not resource_id:
        log.error(u'Please configure index lot resource ID')

    context = {
        u'user': toolkit.c.user
        }

    search_params = dict(resource_id=resource_id, limit=1, )
    search = toolkit.get_action(u'datastore_search')(context, search_params)
    return delimit_number(search.get(u'total', 0))


def get_nhm_organisation_id():
    '''Get the organisation ID for the NHM.

    :returns: ID for the NHM organisation

    '''
    value = toolkit.config.get(u'ldap.organization.id')
    return unicode(value) if value is not None else None


def get_specimen_resource_id():
    '''Get the ID for the specimens dataset.

    :returns: ID for the specimen resource

    '''
    value = toolkit.config.get(u'ckanext.nhm.specimen_resource_id')
    return unicode(value) if value is not None else None


def get_indexlot_resource_id():
    '''Get the ID for the index lots dataset.

    :returns: ID for indexlot resource

    '''
    value = toolkit.config.get(u'ckanext.nhm.indexlot_resource_id')
    return unicode(value) if value is not None else None


@cache_region(u'permanent', u'collection_stats')
def collection_stats():
    '''Get collection stats, grouped by Collection code.'''
    resource_id = get_specimen_resource_id()
    total = 0
    collections = OrderedDict()
    search_params = dict(resource_id=resource_id, limit=0, facets=[u'collectionCode'],
                         facets_limit=5,
                         # Get an extra facet, so we can determine if there are more
                         )

    context = {
        u'user': toolkit.c.user
        }
    try:
        search = toolkit.get_action(u'datastore_search')(context=context,
                                                         data_dict=search_params)
    except SolrException:
        pass
    else:
        for collection_code, num in search[u'facets'][u'facet_fields'][
            u'collectionCode'].items():
            collections[collection_code] = num
            total += num

    stats = {
        u'total': total,
        u'collections': collections
        }
    return stats


def get_department(collection_code):
    '''Return a department name for collection code.

    :param collection_code: BOT, PAL etc.,
    :returns: Full department name - Entomology

    '''
    departments = {
        u'bmnh(e)': u'Entomology',
        u'bot': u'Botany',
        u'min': u'Mineralogy',
        u'pal': u'Palaeontology',
        u'zoo': u'Zoology',
        }

    return departments[collection_code.lower()]


def delimit_number(num):
    '''Separate long number into thousands 1000000 => 1,000,000.

    :param num:

    '''
    return u'{:,}'.format(num)


def api_doc_link():
    '''Link to API documentation.'''
    attr = {
        u'class': u'external',
        u'target': u'_blank'
        }
    return toolkit.h.link_to(toolkit._(u'API guide'),
                             u'http://docs.ckan.org/en/latest/api/index.html', **attr)


def get_google_analytics_config():
    '''Get Google Analytic configuration.'''

    return {
        u'id': toolkit.config.get(u'googleanalytics.id'),
        u'domain': toolkit.config.get(u'googleanalytics.domain', u'auto')
        }


def persistent_follow_button(obj_type, obj_id):
    '''Replaces ckan.lib.follow_button which returns an empty string for anonymous users.
    For anon users this function outputs a follow button which links through
    to the login page

    :param obj_type: 
    :param obj_id: 
    :returns:

    '''
    obj_type = obj_type.lower()
    assert obj_type in toolkit.h._follow_objects

    if toolkit.c.user:
        context = {
            u'user': toolkit.c.user
            }
        action = u'am_following_%s' % obj_type
        following = toolkit.get_action(action)(context, {
            u'id': obj_id
            })
        return toolkit.h.snippet(u'snippets/follow_button.html', following=following,
                                 obj_id=obj_id, obj_type=obj_type)

    return toolkit.h.snippet(u'snippets/anon_follow_button.html', obj_id=obj_id,
                             obj_type=obj_type)


def filter_resource_items(key):
    '''Filter resource items - if key is in blacklist, return false

    :param key: return: boolean
    :returns: boolean

    '''

    blacklist = [u'image field', u'title field', u'datastore active', u'has views',
                 u'on same domain', u'resource group id', u'revision id', u'url type']

    return key.strip() not in blacklist


def get_map_styles():
    '''New map config overriding the marker point img'''
    return {
        u'point': {
            u'iconUrl': u'/images/leaflet/marker.png',
            u'iconSize': [20, 34],
            u'iconAnchor': [12, 30]
            }
        }


def get_query_params():
    '''Helper function to build a dict of query params
    To be used in urls for persistent filters


    :returns: dict

    '''
    params = dict()

    for key in [u'q', u'filters']:
        value = toolkit.request.params.get(key)
        if value:
            params[key] = value

    return params


def resource_view_get_field_groups(resource):
    '''Return dictionary of field groups

    :param resource: resource dict
    :returns: OrderedDict of fields

    '''
    view_cls = resource_view_get_view(resource)

    return view_cls.get_field_groups(resource)


# Resource view and filters
def resource_view_state(resource_view_json, resource_json):
    '''Alter the recline view resource, adding in state info

    :param resource_view_json: return:
    :param resource_json: 

    '''
    resource_view = json.loads(resource_view_json)
    resource = json.loads(resource_json)

    # There is an annoying feature/bug in slickgrid, that if fitColumns=True
    # And grid is wider than available viewport, slickgrid columns cannot
    # Be resized until fitColumns is deactivated
    # So to fix, we're going to work out how many columns are in the dataset
    # To decide whether or not to turn on fitColumns
    # Messy, but better than trying to hack around with slickgrid

    fields = toolkit.h.resource_view_get_fields(resource)

    num_fields = len(fields)

    viewport_max_width = 920
    col_width = 100
    fit_columns = (num_fields * col_width) < viewport_max_width

    # Initiate the resource view
    view = resource_view_get_view(resource)

    # And get the state
    resource_view[u'state'] = view.get_slickgrid_state()

    # TODO: This can be merged into get_slickgrid_state
    resource_view[u'state'][u'fitColumns'] = fit_columns

    # ID and DQI always first
    columns_order = [u'_id']
    if u'gbifIssue' in fields:
        columns_order.append(u'gbifIssue')
    # Add the rest of the columns to the columns order
    columns_order += [f for f in fields if f not in columns_order]
    resource_view[u'state'][u'columnsOrder'] = list(columns_order)

    if view.grid_column_widths:
        for column, width in view.grid_column_widths.items():
            resource_view[u'state'][u'columnsWidth'].append({
                u'column': column,
                u'width': width
                })

    try:
        return json.dumps(resource_view)
    except TypeError:
        return {}


def resource_is_dwc(resource):
    '''Is the resource format DwC?

    :param resource: return:

    '''
    return bool(resource.get(u'format').lower() == u'dwc')


def camel_case_to_string(camel_case_string):
    '''

    :param camel_case_string: 

    '''
    s = u' '.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', camel_case_string))
    return s[0].upper() + s[1:]


def get_resource_filter_options(resource, resource_view):
    '''Return the available filter options for the given resource

    :param resource: Dictionary representing a resource
    :param resource_view: 
    :returns: A dictionary associating each option's name to a dict
            defining:
                - label: The label to display to users;
                - checked: True if the option is currently applied.

    '''
    options = resource_view_get_filter_options(resource)
    filter_list = toolkit.request.params.get(u'filters', u'').split(u'|')
    filters = {}

    # If this is a gallery view, hide the has image filter
    # Only records with images will be displayed anyway
    # if resource_view['view_type'] == 'gallery':
    #     options.pop("_has_image", None)

    for filter_def in filter_list:
        try:
            (key, value) = filter_def.split(u':', 1)
        except ValueError:
            continue

        if key not in filters:
            filters[key] = [value]
        else:
            filters[key].append(value)
    result = {}
    for o in options:
        if options[o].get(u'hide', False):
            continue
        result[o] = options[o]
        result[o][u'checked'] = o in filters and u'true' in filters[o]
    return result


def get_resource_gbif_errors(resource):
    '''Return GBIF errors applicable for this resource
    i.e. if this the specimen resource, return the gbif errors dict

    :param resource: return:

    '''

    # If this is a
    if resource.get(u'id') == get_specimen_resource_id():
        return GBIF_ERRORS
    else:
        return {}


def get_allowed_view_types(resource, package):
    '''Overwrite ckan.lib.helpers.get_allowed_view_types
    We want to edit some of the options - remove Image and change Tiled Map to Map

    :param resource: param package:
    :param package: 

    '''

    view_types = toolkit.h.get_allowed_view_types(resource, package)
    blacklisted_types = [u'image']

    filtered_types = []

    for view_type in view_types:
        # Exclude blacklisted types (at the moment just Image)
        if view_type[0] in blacklisted_types:
            continue

        # Rename Tiled map => map
        if view_type[1] == u'Tiled map':
            view_type = (view_type[0], u'Map', view_type[2])

        filtered_types.append(view_type)

    return filtered_types


def get_facet_label_function(facet_name, multi=False):
    '''For a given facet, return the function used to fetch the facet's items labels

    :param facet_name: Facet name
    :param multi: If True, the function returned should take a list of facets and a filter value to find the matching
                  facet on the name field (optional, default: False)
    :returns: A function or None

    '''
    facet_function = None
    if facet_name == u'creator_user_id':
        facet_function = get_creator_id_facet_label

    if facet_function and multi:
        def filter_facets(facet, filter_value):
            '''

            :param facet: 
            :param filter_value: 

            '''
            for f in facet:
                if f[u'name'] == filter_value:
                    return facet_function(f)
            return filter

        return filter_facets
    else:
        return facet_function


def get_creator_id_facet_label(facet):
    '''Return display name for the creator_id facet

    :param facet: A dictionary representing a single value for the facet
    :returns: A string to use for display name

    '''
    try:
        user = model.User.get(facet[u'name'])
        display_name = user.display_name
    except (toolkit.ObjectNotFound, AttributeError) as e:
        display_name = facet[u'display_name']
    return display_name


def field_name_label(field_name):
    '''Convert a field name into a label - replacing _s and upper casing first character

    :param field: return: str label
    :param field_name: 
    :returns: str label

    '''
    label = field_name.replace(u'_', u' ')
    label = label[0].upper() + label[1:]
    return label


def field_is_link(value):
    '''Is a field a link (starts with http and is a valid URL)

    :param value: return: boolean
    :returns: boolean

    '''
    try:
        return value.startswith(u'http') and re_url_validation.match(value)
    except Exception:
        pass
    return False


def get_contact_form_params(pkg=None, res=None, rec=None):
    '''Get a list of IDS

    :param pkg: param res: (optional, default: None)
    :param rec: return: (optional, default: None)
    :param res:  (optional, default: None)

    '''

    params = {}

    if pkg:
        params[u'package_id'] = pkg.get(u'id')

    if res:
        params[u'resource_id'] = res.get(u'id')

    if rec:
        params[u'record_id'] = rec.get(u'_id')

    return params


def get_contact_form_template_url(params):
    '''Build a URL suitable for linking to the contact form snippet
    
    For example: /api/1/util/snippet/contact_form.html?resource_id=123&record_id456
    
    Can be parsed output from get_contact_form_params

    :param params: return:

    '''

    url = u'/api/1/util/snippet/contact_form.html'

    if params:
        url += u'?%s' % urllib.urlencode(params)

    return url


def get_contact_form_department_options():
    '''Contact form category'''
    return list_to_form_options(COLLECTION_CONTACTS.keys())


def downloadable(resource):
    '''Is a resource downloadable

    :param resource: return: bool
    :returns: bool

    '''
    return bool(resource[u'format'])


def is_sysadmin():
    '''Is user a sysadmin user'''
    if toolkit.c.userobj.sysadmin:
        return True


def record_display_field(field_name, value):
    '''Decide whether to display a field
    Evaluates whether a field has value

    :param field_name: param value:
    :param value: 
    :returns: bool - true to display field; false not to

    '''

    # If this is a string, strip it before evaluating
    if isinstance(value, basestring):
        value = value.strip()

    return bool(value)


def group_fields_have_data(record_dict, fields):
    '''Are any of the fields in the group populated
    Return true if they are; false if not

    :param record_dict: record data
    :param fields: fields to test
    :returns: bool

    '''

    for field in fields:
        if record_dict.get(field, None):
            return True


def get_image_licence_options():
    '''Return list of image licences
    Currently this is the same list as dataset licences


    '''

    licenses = [(u'', u'')] + model.Package.get_license_options()

    # Format licences as form options list of dicts
    return [{
        u'value': value,
        u'text': text
        } for text, value in licenses]


def social_share_text(pkg_dict=None, res_dict=None, rec_dict=None):
    '''Generate social share text for a package

    :param pkg_dict: return: (optional, default: None)
    :param res_dict:  (optional, default: None)
    :param rec_dict:  (optional, default: None)

    '''

    text = list()

    if rec_dict:

        try:
            title = rec_dict.get(res_dict[u'_title_field'], None) or u'Record %s' % \
                    rec_dict[u'_id']
        except KeyError:
            title = u'Record %s' % rec_dict[u'_id']

        text.append(title)

    elif res_dict:
        text.append(u'%s' % (res_dict[u'name']))
    elif pkg_dict:
        text.append(u'%s' % (pkg_dict[u'title'] or pkg_dict[u'name']))

    text.append(u'on the @NHM_London Data Portal')

    try:
        text.append(u'DOI: %s' % os.path.join(u'https://doi.org', pkg_dict[u'doi']))
    except KeyError:
        pass

    text = u' '.join(text)

    return urllib.quote(text.encode(u'utf8'))


def accessible_gravatar(email_hash, size=100, default=None, userobj=None):
    '''Port of ckan helper gravatar
    Adds title text to the image so it passes accessibility checks

    :param email_hash: param size:
    :param default: param userobj: (optional, default: None)
    :param size:  (optional, default: 100)
    :param userobj:  (optional, default: None)

    '''
    if default is None:
        default = toolkit.config.get(u'ckan.gravatar_default', u'identicon')

    if not default in toolkit.h._VALID_GRAVATAR_DEFAULTS:
        # treat the default as a url
        default = urllib.quote(default, safe=u'')

    return literal(u'''<img alt="%s" src="//gravatar.com/avatar/%s?s=%d&amp;d=%s"
        class="gravatar" width="%s" height="%s" />''' % (
        userobj.name, email_hash, size, default, size, size))


def dataset_author_truncate(author_str):
    '''For author strings with lots of authors need to shorten for display
    insert et al as abbreviation tag

    :param author_str: dataset author
    :returns: shortened author str, will full text in abbr tag

    '''

    def _truncate(author_str, separator=None):
        '''

        :param author_str: 
        :param separator:  (optional, default: None)

        '''

        # If we have a separator, split string on it
        if separator:
            shortened = u';'.join(author_str.split(separator)[0:4])
        else:
            # Otherwise use the jinja truncate function (may split author name)
            shortened = do_truncate(author_str, length=AUTHOR_MAX_LENGTH, end=u'')

        return literal(
            u'{0} <abbr title="{1}" style="cursor: pointer;">et al.</abbr>'.format(
                shortened, author_str))

    if author_str and len(author_str) > AUTHOR_MAX_LENGTH:

        if u';' in author_str:
            author_str = _truncate(author_str, u';')
        elif u',' in author_str:
            author_str = _truncate(author_str, u',')
        else:
            author_str = _truncate(author_str)

    return author_str


def get_resource_facets(resource):
    '''Return a list of facets for a particular resource

    :param resource: return:

    '''
    # Number of facets to display
    num_facets = 10
    resource_view = resource_view_get_view(resource)
    # If facets aren't defined in the resource view, then just return
    if not resource_view.field_facets:
        return
    context = {
        u'user': toolkit.c.user
        }
    # Build query parameters for the faceted search
    # We'll use the same query parameters used in the current request
    # And then add extras to perform a solr faceted query, returning
    # facets but zero results (limit=0)
    query_params = get_query_params()

    # Convert filters to a dictionary as this won't happen automatically
    # as we're retrieving raw get parameters from get_query_params
    filters = {}
    if query_params.get(u'filters'):
        for f in query_params.get(u'filters').split(u'|'):
            filter_field, filter_value = f.split(u':', 1)
            filters.setdefault(filter_field, []).append(filter_value)

    search_params = dict(resource_id=resource.get(u'id'), limit=0,
                         facets=resource_view.field_facets,
                         q=query_params.get(u'q', None), filters=filters,
                         facets_limit=num_facets + 1,
                         # Get an extra facet, so we can determine if there are more
                         )

    for field_name in resource_view.field_facets:
        if toolkit.h.get_param_int(u'_%s_limit' % field_name) == 0:
            search_params.setdefault(u'facets_field_limit', {})[field_name] = 50

    search = toolkit.get_action(u'datastore_search')(context, search_params)
    facets = []

    # dictionary of facet name => formatter function with camel_case_to_string defined
    # as the default formatting function and then any overrides for specific edge cases
    facet_label_formatters = defaultdict(lambda: camel_case_to_string, **{
        # specific lambda for GBIF to ensure it's capitalised correctly
        u'gbifIssue': lambda _: u'GBIF Issue'
        })

    # Dictionary of field name => formatter function
    # Pass facet value to a formatter to get a better facet item label
    facet_field_label_formatters = {
        u'collectionCode': get_department
        }

    # Loop through original facets to ensure order is preserved
    for field_name in resource_view.field_facets:
        # Parse the facets into a list of dictionary values, similar to that
        # Built for the dataset search solr facets
        active_facet = field_name in filters
        facet = {
            u'name': field_name,
            u'label': facet_label_formatters[field_name](field_name),
            u'facet_values': [],
            u'has_more': len(search[u'facets'][u'facet_fields'][
                                 field_name]) > num_facets and field_name not in
                         search_params.get(
                u'facets_field_limit', {}),
            u'active': active_facet
            }

        for value, count in search[u'facets'][u'facet_fields'][field_name].items():
            label = value
            try:
                label = facet_field_label_formatters[field_name](label)
            except KeyError:
                pass
            facet[u'facet_values'].append({
                u'name': value,
                u'label': label,
                u'count': count,
                })

        facet[u'facet_values'] = sorted(facet[u'facet_values'], key=itemgetter(u'count'),
                                        reverse=True)
        # If this is the active facet, only show the highest item
        if active_facet:
            facet[u'facet_values'] = facet[u'facet_values'][:1]
        # Slice the facet values, so length matches num_facets - need to do this after
        #  the key sort
        if facet[u'has_more']:
            facet[u'facet_values'] = facet[u'facet_values'][0:num_facets]
        facets.append(facet)

    return facets


def remove_url_filter(field, value, extras=None):
    '''The CKAN built in functions remove_url_param / add_url_param cannot handle
    multiple filters which are concatenated with |, not separate query params
    This replaces remove_url_param for filters

    :param field: param value:
    :param extras: return: (optional, default: None)
    :param value: 

    '''

    # import copy
    # params = copy.copy(dict(request.params))

    params = dict(toolkit.request.params)
    try:
        del params[u'filters']
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
                filter_parts.append(u'%s:%s' % (filter_field, filter_value))
        # If we have filter parts, add them back to the params dict
        if filter_parts:
            params[u'filters'] = u'|'.join(filter_parts)
    return _create_filter_url(params, extras)


def add_url_filter(field, value, extras=None):
    '''The CKAN built in functions remove_url_param / add_url_param cannot handle
    multiple filters which are concatenated with |, not separate query params
    This replaces remove_url_param for filters

    :param field: param field:
    :param extras: return: (optional, default: None)
    :param value: 

    '''

    params = dict(toolkit.request.params)
    url_filter = u'%s:%s' % (field, value)
    if params.get(u'filters', None):
        params[u'filters'] += u'|%s' % url_filter
    else:
        params[u'filters'] = url_filter

    return _create_filter_url(params, extras)


def _create_filter_url(params, extras=None):
    '''Helper function to create filter URL

    :param params: param extras:
    :param extras:  (optional, default: None)

    '''
    params_no_page = [(k, v) for k, v in params.items() if k != u'page']
    return toolkit.h._create_url_with_params(list(params_no_page), extras=extras)


def parse_request_filters():
    '''Get the filters from the request object'''
    filter_dict = {}

    try:
        filter_params = toolkit.request.params.get(u'filters').split(u'|')
    except AttributeError:
        return {}

    # Remove empty values form the filter_params
    filter_params = filter(None, filter_params)

    for filter_param in filter_params:
        field, value = filter_param.split(u':', 1)
        filter_dict.setdefault(field, []).append(value)

    return filter_dict


def get_resource_filter_pills(package, resource, resource_view=None):
    '''Get filter pills
    We don't want the field group pills - these are handled separately in
    get_resource_field_groups

    :param resource: param package:
    :param package: 
    :param resource_view:  (optional, default: None)

    '''

    filter_dict = parse_request_filters()
    extras = {
        u'id': package[u'id'],
        u'resource_id': resource[u'id']
        }

    pills = []

    for filter_field, filter_value in filter_dict.items():
        # If the field name stars with an underscore, don't include it in the pills
        if filter_field.startswith(u'_'):
            continue
        # Remove filter from url function
        href = remove_url_filter(filter_field, filter_value, extras=extras)
        pills.append({
            u'label': camel_case_to_string(filter_field),
            u'field': filter_field,
            u'value': u' '.join(filter_value),
            u'href': href
            })

    return pills


def resource_view_get_filterable_fields(resource):
    '''

    :param resource: 

    '''

    filterable_field_types = [u'int', u'text', u'numeric']

    if not resource.get(u'datastore_active'):
        return []

    data = {
        u'resource_id': resource[u'id'],
        u'limit': 0,
        # As these are for the filters, only get the indexed fields
        u'indexed_only': True
        }

    result = toolkit.get_action(u'datastore_search')({}, data)

    fields = [f[u'id'] for f in result.get(u'fields', []) if
              f[u'type'] in filterable_field_types]
    return sorted(fields)


def form_select_datastore_field_options(resource, allow_empty=True):
    '''

    :param resource: 
    :param allow_empty:  (optional, default: True)

    '''
    fields = toolkit.h.resource_view_get_fields(resource)
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
        update_dates = filter(None,
                              [toolkit.h._datestamp_to_datetime(resource[field]) for
                               field in fields])
        # return the latest non-None value, or None
        return max(update_dates) if update_dates else None

    # find the latest update date for each resource using the above function and
    # then filter out the ones that don't have an update date available
    dates_and_names = filter(lambda x: x[0],
                             [(get_resource_last_update(r), r[u'name']) for r in
                              pkg_dict[u'resources']])
    if dates_and_names:
        # find the most recent date and name combo
        date, name = max(dates_and_names, key=lambda x: x[0])
        return u'{} ({})'.format(
            toolkit.h.render_datetime(date, date_format=date_format), name)
    # there is no available update so we return 'unknown'
    return toolkit._(u'unknown')


def get_external_links(record):
    '''
    Helper called on collection record pages (i.e. records in the specimens, indexlots
    or artefacts resources) which is
    expected to return a list of tuples. Each tuple provides a title and a list of
    links, respectively, which are
    relevant to the record.
    :param record:
    :return:
    '''
    sites = external_links.get_relevant_sites(record)
    ranks = extract_ranks(record)
    if ranks:
        return [(name, icon, OrderedDict.fromkeys(
            [(rank, link.format(rank)) for rank in ranks.values()]))
                for name, icon, link in sites]
    return []
