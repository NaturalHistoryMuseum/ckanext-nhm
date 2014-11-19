import os
import re
import ckan.plugins as p
import ckan.logic as logic
import ckan.model as model
from ckan.common import c, request
from ckan.lib.helpers import url_for
from itertools import chain
import ckan.lib.navl.dictization_functions as dictization_functions
import ckanext.nhm.logic.action as action
import ckanext.nhm.logic.schema as nhm_schema
import ckanext.nhm.lib.helpers as helpers
from ckanext.nhm.lib.resource_filters import resource_filter_options, FIELD_DISPLAY_FILTER
from ckanext.contact.interfaces import IContact
from ckanext.datastore.interfaces import IDatastore
from collections import OrderedDict
from pylons import config

get_action = logic.get_action

unflatten = dictization_functions.unflatten

Invalid = p.toolkit.Invalid

# Contact addresses to route specimen contact request to
collection_contacts = {
    'Entomology': 'b.scott@nhm.ac.uk',
    'Botany': 'b.scott@nhm.ac.uk',
    'Mineralogy': 'b.scott@nhm.ac.uk',
    'Palaeontology': 'b.scott@nhm.ac.uk',
    'Zoology': 'b.scott@nhm.ac.uk'
}


class NHMPlugin(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    """
    NHM CKAN modifications
        View individual records in a dataset
        Set up NHM (CKAN) model
    """
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IFacets, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(IDatastore)
    p.implements(IContact)

    ## IConfigurer
    def update_config(self, config):

        # Add template directory - we manually add to extra_template_paths
        # rather than using add_template_directory to ensure it is always used
        # to override templates
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(root_dir, 'ckanext', 'nhm', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir, config.get('extra_template_paths', '')])

        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-nhm')
        p.toolkit.add_resource('theme/fanstatic', 'ckanext-nhm-fanstatic')

        # Add another public directory for dataset files - this will hopefully be temporary, until DAMS
        p.toolkit.add_public_directory(config, 'files')

    ## IRoutes
    def before_map(self, map):

        specimen_resource_id = helpers.get_specimen_resource_id()
        indexlot_resource_id = helpers.get_indexlot_resource_id()

        # Add controller for KE EMu specimen records
        map.connect('specimen', '/dataset/{package_name}/resource/%s/record/{record_id}' % specimen_resource_id,
                    controller='ckanext.nhm.controllers.specimen:SpecimenController',
                    action='view', resource_id=specimen_resource_id)

        # # Add controller for KE EMu Index Lot records
        # map.connect('indexlots', '/dataset/{package_name}/resource/%s/record/{record_id}' % indexlot_resource_id,
        #             controller='ckanext.nhm.controllers.indexlot:IndexLotController',
        #             action='view', resource_id=indexlot_resource_id)

        # Add view record
        map.connect('record', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}',
                    controller='ckanext.nhm.controllers.record:RecordController',
                    action='view')

        # Add dwc view
        map.connect('dwc', '/dataset/{package_name}/resource/{resource_id}/record/{record_id}/dwc',
                    controller='ckanext.nhm.controllers.dwc:DarwinCoreController',
                    action='view')

        # About pages
        map.connect('about_citation', '/about/citation', controller='ckanext.nhm.controllers.about:AboutController', action='citation')
        map.connect('about_download', '/about/download', controller='ckanext.nhm.controllers.about:AboutController', action='download')
        map.connect('about_licensing', '/about/licensing', controller='ckanext.nhm.controllers.about:AboutController', action='licensing')
        map.connect('about_credits', '/about/credits', controller='ckanext.nhm.controllers.about:AboutController', action='credits')

        # Legal pages
        map.connect('legal_privacy', '/privacy', controller='ckanext.nhm.controllers.legal:LegalController', action='privacy')
        map.connect('legal_terms', '/terms-conditions', controller='ckanext.nhm.controllers.legal:LegalController', action='terms')

        # About stats pages
        map.connect('stats_datasets', '/about/statistics/datasets', controller='ckanext.nhm.controllers.stats:StatsController', action='datasets', ckan_icon='bar-chart')
        map.connect('stats_contributors', '/about/statistics/contributors', controller='ckanext.nhm.controllers.stats:StatsController', action='contributors', ckan_icon='user')
        map.connect('stats_records', '/about/statistics/records', controller='ckanext.nhm.controllers.stats:StatsController', action='records', ckan_icon='file-text')

        # Dataset metrics
        map.connect('dataset_metrics', '/dataset/metrics/{id}', controller='ckanext.nhm.controllers.stats:StatsController', action='dataset_metrics', ckan_icon='bar-chart')

        return map

    # IActions
    def get_actions(self):

        return {
            'record_get':  action.record_get
        }

    # ITemplateHelpers
    def get_helpers(self):

        h = {}

        #  Build a list of helpers from import ckanext.nhm.lib.helpers as nhmhelpers
        for helper in dir(helpers):

            #  Exclude private
            if not helper.startswith('_'):
                func = getattr(helpers, helper)

                #  Ensure it's a function
                if hasattr(func, '__call__'):
                    h[helper] = func

        return h

    ## IDatasetForm - CKAN Metadata
    def package_types(self):
        return []

    def is_fallback(self):
        return True

    def create_package_schema(self):
        return nhm_schema.create_package_schema()

    def update_package_schema(self):
        return nhm_schema.update_package_schema()

    def show_package_schema(self):
        return nhm_schema.show_package_schema()

    ## IFacets
    def dataset_facets(self, facets_dict, package_type):

        # Remove organisations and groups
        del facets_dict['organization']
        del facets_dict['groups']

        # Add author facet as the first item
        facets_dict = OrderedDict([('author', 'Authors')] + facets_dict.items())
        facets_dict['creator_user_id'] = 'User'

        return facets_dict

    ## IPackageController
    def before_search(self, data_dict):
        # If there's no sort criteria specified, default to promoted and last modified
        if not data_dict.get('sort', None):
            data_dict['sort'] = u'promoted asc, metadata_modified desc'

        return data_dict

    ## IDataStore
    def datastore_validate(self, context, data_dict, all_field_ids):
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            # Remove both filter options and field groups from filters
            # These will be handled separately
            options = chain(resource_filter_options(resource).keys(), [FIELD_DISPLAY_FILTER])
            for o in options:
                if o in data_dict['filters']:
                    del data_dict['filters'][o]

        return data_dict

    def datastore_search(self, context, data_dict, all_field_ids, query_dict):

        try:
            print request.headers['Referer']
        except:
            pass

        # print context
        # print data_dict

        # field_group = core, taxonomy, botany etc.,

        # TODO: Add field group

        # query_dict['select'] = ['"Catalog number"', '"_id"']

        # request_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(request.params))))
        # # print request_dict
        #
        # for i in dir(request):
        #     print getattr(request, i)

        # print request.query_string

        # Add our options filters
        if 'filters' in data_dict:
            resource_show = p.toolkit.get_action('resource_show')
            resource = resource_show(context, {'id': data_dict['resource_id']})
            options = resource_filter_options(resource)
            for o in options:
                if o in data_dict['filters'] and 'true' in data_dict['filters'][o]:
                    if 'sql' in options[o]:
                        query_dict['where'].append(options[o]['sql'])
                elif 'sql_false' in options[o]:
                    query_dict['where'].append(options[o]['sql_false'])

        # Enhance the full text search, by adding support for double quoted expressions. We leave the
        # full text search query intact (so we benefit from the full text index) and add an additonal
        # LIKE statement for each quoted group.
        if 'q' in data_dict and not isinstance(data_dict['q'], dict):
            for match in re.findall('"[^"]+"', data_dict['q']):
                query_dict['where'].append((
                    '"{}"::text LIKE %s'.format(resource['id']),
                    '%' + match[1:-1] + '%'
                ))

        # CKAN's field auto-completion uses full text search on individual fields. This causes
        # problems because of stemming issues, and is quite slow on our data set (even with an
        # appropriate index). We detect this type of queries and replace them with a LIKE query.
        if 'q' in data_dict and isinstance(data_dict['q'], dict) and len(data_dict['q']) == 1:
            field_name = data_dict['q'].keys()[0]
            if data_dict['fields'] == field_name and data_dict['q'][field_name].endswith(':*'):
                escaped_field_name = '"' + field_name.replace('"', '') + '"'
                value = '%' + data_dict['q'][field_name].replace(':*', '%')
                query_dict = {
                    'distinct': True,
                    'limit': query_dict['limit'],
                    'offset': query_dict['offset'],
                    'sort': [escaped_field_name],
                    'where': [(escaped_field_name + '::citext LIKE %s', value)],
                    'select': [escaped_field_name],
                    'ts_query': ''
                }
        return query_dict

    def datastore_delete(self, context, data_dict, all_field_ids, query_dict):
        return query_dict

    ## IContact
    def mail_alter(self, mail_dict, data_dict):

        specimen_resource_id = helpers.get_specimen_resource_id()
        indexlot_resource_id = helpers.get_indexlot_resource_id()

        # Get the submitted data values
        package_id = data_dict.get('package_id', None)
        resource_id = data_dict.get('resource_id', None)
        record_id = data_dict.get('record_id', None)

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        # URL to provide as link to contact email body
        # Over written by linking to record / resource etc., - see below
        url = None

        # If we have a record ID, this is a contact/form request from a record page
        if record_id and resource_id in [specimen_resource_id, indexlot_resource_id]:

            # Load the record to retrieve the collection code
            record_dict = get_action('record_get')(context, {'resource_id': resource_id, 'record_id': record_id})

            if resource_id == specimen_resource_id:
                department = helpers.get_department(record_dict.get('Collection code'))
                named_route = 'specimen'
                mail_dict['subject'] = 'Specimen enquiry'
            else:
                department = record_dict.get('Department')
                named_route = 'indexlot'
                mail_dict['subject'] = 'Index lot enquiry'

            # Add the specific email contact to the built in one (data@nhm.ac.uk)
            mail_dict['recipient_email'] += ', ' + collection_contacts[department]
            mail_dict['recipient_name'] = '%s collection manager' % department

            url = url_for(named_route, action='view', package_name=package_id, resource_id=resource_id, record_id=record_id, qualified=True)

        else:  # Not a specimen or indexlot record

            # If we have a package ID, load the package
            if package_id:

                package_dict = get_action('package_show')(context, {'id': package_id})
                # Load the user - using model rather user_show API which loads all the users packages etc.,
                user_obj = model.User.get(package_dict['creator_user_id'])

                # Update send to with creator username
                mail_dict['recipient_email'] += ', ' + user_obj.email
                mail_dict['subject'] = 'Message regarding dataset: %s' % package_dict['title']

                if resource_id:

                    if record_id:
                        url = url_for('record', action='view', package_name=package_id, resource_id=resource_id, record_id=record_id, qualified=True)
                    else:
                        url = url_for(controller='package', action='resource_read', id=package_id, resource_id=resource_id, qualified=True)

                else:
                    url = url_for(controller='package', action='read', id=package_id, qualified=True)

        # If we have a URL append it to the message body
        if url:
            mail_dict['body'] += '\n' + url

        return mail_dict