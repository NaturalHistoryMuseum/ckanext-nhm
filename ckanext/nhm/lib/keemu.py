#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""
import sys
import itertools
import abc
import inspect
import logging
import json
from collections import OrderedDict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import select, join
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import Table, Column, Integer, func, literal_column, case, or_, text, desc, union_all, not_, cast
from sqlalchemy.schema import MetaData
import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from pylons import config
from ckanext.nhm.lib.db import get_datastore_session, CreateAsSelect, InsertFromSelect
from ke2sql.model.keemu import *
from ke2sql.model.keemu import specimen_sex_stage, catalogue_associated_record, catalogue_multimedia, specimen_mineralogical_age

log = logging.getLogger(__name__)

MULTIMEDIA_URL = 'http://www.nhm.ac.uk/emu-classes/class.EMuMedia.php?irn=%s&image=yes'

INSTITUTION_CODE = 'NHMUK'
IDENTIFIER_PREFIX = '%s:ecatalogue:' % INSTITUTION_CODE

VIEW = 'VIEW'
MATERIALIZED_VIEW = 'MATERIALIZED VIEW'
TABLE = 'TABLE'

Base = declarative_base()

# TODO: Plug into tasks

class KeEMuDatastore(object):
    """
    Base class for KE EMu Datastore
    """
    __metaclass__ = abc.ABCMeta

    default_package_params = {
        'author': None,
        'author_email': None,
        'license_id': u'other-open',
        'maintainer': None,
        'maintainer_email': None,
        'resources': [],
    }

    format = 'csv'  # Default format is CSV
    session = None
    # Fields to exclude from the _full_text index
    full_text_blacklist = []

    # Fields to index (in addition to primary key)
    index_fields = []

    geom_columns = None

    def __init__(self):
        self.session = get_datastore_session()
        self.metadata = MetaData(self.session.bind)

    @abc.abstractproperty
    def name(self):
        return None

    @abc.abstractproperty
    def description(self):
        return None

    @abc.abstractproperty
    def package(self):
        return None

    @abc.abstractproperty
    def datastore_query(self):
        """
        Return the select query to create the datastore
        """
        return None

    def view_exists(self, view_name):
        return self.session.execute("SELECT EXISTS (select 1 from pg_class where relname = '{view_name}')".format(view_name=view_name)).scalar()

    def table_exists(self, table_name):
        return self.session.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')".format(table_name=table_name)).scalar()

    def create_package(self, context):
        """
        Setup the CKAN datastore
        Return the package
        @param context:
        @return: package
        """
        #  Merge package params with default params
        params = dict(itertools.chain(self.default_package_params.iteritems(), self.package.iteritems()))

        try:

            # Try and load the KE EMu package
            package = logic.get_action('package_show')(context, {'id': params['name']})

        except logic.NotFound:

            # KE EMu package not found; create it
            # Error adds dataset_show to __auth_audit: remove it
            context['__auth_audit'] = []
            package = logic.get_action('package_create')(context, params)

        return package

    def create_datastore_resource(self):
        """
        Create the CKAN datastore resource
        @return: resource_id
        """

        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}

        # Create a package for the new datastore
        package = self.create_package(context)

        log.info('Creating package %s: SUCCESS', self.name)

        # Get all existing resources keyed by name
        existing_resources = {r['name']: r for r in package['resources']}

        try:

            resource_id = existing_resources[self.name]['id']

        except KeyError:  # We don't have a datastore resource so create one

            # Create the datastore itself
            datastore_params = {
                'records': [],
                'resource': {
                    'name': self.name,
                    'description': self.description,
                    'package_id': package['id'],
                    'format': self.format
                }
            }

            datastore = logic.get_action('datastore_create')(context, datastore_params)
            resource_id = datastore['resource_id']

        log.info('Creating datastore %s: SUCCESS', resource_id)

        return resource_id

    def build_source_table(self, resource_id):
        """
        Build a table to use as a source for the materialised view

        @param resource_id: CKAN UUID for the dataset resource
        @return: SQLA object representing the source table
        """
        source_table_name = '_source_%s' % resource_id

        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}

        datastore_query = self.datastore_query()

        try:

            source_table = Table(source_table_name, self.metadata, autoload=True)

            # Source table exists
            # Remove existing data
            self.session.execute(text('TRUNCATE TABLE "{source_table_name}"'.format(source_table_name=source_table_name)))

            log.info('Deleting existing records: SUCCESS')

            # Set geometry columns to null
            if self.geom_columns is not None:
                datastore_query = datastore_query.column(literal_column("NULL").label(config.get('map.geom_field_4326', '_geom')))
                datastore_query = datastore_query.column(literal_column("NULL").label(config.get('map.geom_field', '_the_geom_webmercator')))

            # Ensure columns match
            assert [c.key for c in datastore_query.c] == [c.key for c in source_table.c]

            #  INSERT INTO source_table (copy_columns) (SELECT ... datastore_query)
            q = InsertFromSelect(source_table, datastore_query)

            self.session.execute(q)
            self.session.commit()

            log.info('Updating source table: SUCCESS')

            # Update geometry columns
            if self.geom_columns is not None:
                update_geom_columns = toolkit.get_action('update_geom_columns')
                update_geom_columns(context, {
                    'resource_id': source_table_name,
                    'lat_field': self.geom_columns['lat_field'],
                    'long_field': self.geom_columns['long_field']
                })

                log.info('Updating geometry: SUCCESS')

        except NoSuchTableError:

            # If table doesn't exist create it
            q = CreateAsSelect(source_table_name, datastore_query)
            self.session.execute(q)
            self.session.commit()

            # Add geometry columns
            if self.geom_columns is not None:
                create_geom_columns = toolkit.get_action('create_geom_columns')
                create_geom_columns(context, {
                    'resource_id': source_table_name,
                    'lat_field': self.geom_columns['lat_field'],
                    'long_field': self.geom_columns['long_field']
                })

            # Reflect the new source table
            source_table = Table(source_table_name, self.metadata, autoload=True)

            log.info('Creating source table: SUCCESS')

        return source_table

    def get_full_text_fields(self, source_table):
        """
        Concatenated list of text fields fields to include in _full_text index
        @return: string
        """

        # Get the information schema table
        information_schema = Table('columns', self.metadata, autoload=True, schema='information_schema')

        q = select([
            func.string_agg(func.quote_ident(information_schema.c.column_name), literal_column("', '"))
            ])

        q = q.where(information_schema.c.table_name == source_table.name)

        # We only want varchar and text types
        q = q.where(information_schema.c.data_type.in_(['character varying', 'text']))

        if self.full_text_blacklist:
            q = q.where(not_(information_schema.c.column_name.in_(self.full_text_blacklist)))

        return self.session.execute(q).scalar()

    def materialize_resource(self, resource_id, source_table):
        """
        Create / refresh the materialised view of the dataset
        @param resource_id: CKAN UUID for the dataset resource
        @param source_table: SQLA table object
        @return: None
        """

        # Drop the table created by CKAN - we're going to replace it with a Materialised view
        # Check if table exists before dropping
        # Need to manually check existence, as we will get an error if it's already a view
        if self.table_exists(resource_id):
            self.session.execute('DROP TABLE "{resource_id}"'.format(resource_id=resource_id))

        # Get all text fields to use in the _full_index
        full_text_fields = self.get_full_text_fields(source_table)

        # At this point, all of the source tables are in place
        # So create or refresh the materialised view
        if self.view_exists(resource_id):

            # Just refresh the materialised view
            # This was there will be no downtime for the front end user
            # Table will be unresponsive for the ~1 second it takes to refresh
            self.session.execute(text('REFRESH MATERIALIZED VIEW "{resource_id}"'.format(resource_id=resource_id)))

        else:
            # Create materialised view query

            # All the columns in the source table, except any _index ones
            columns = [column for column in source_table.c if column.key is not '_index']

            view_q = select(columns)
            view_q = view_q.column(
                func.to_tsvector(
                    literal_column("ARRAY_TO_STRING(ARRAY[%s], ' ')" % full_text_fields)
                ).label('_full_text')
            )

            # Create the view
            self.session.execute('CREATE MATERIALIZED VIEW "{resource_id}" AS ({view_q})'.format(resource_id=resource_id, view_q=view_q))

            #  Create primary key (_id) index
            self.session.execute('CREATE UNIQUE INDEX "{resource_id}_id_idx" ON "{resource_id}" (_id)'.format(resource_id=resource_id,))

            # Create additional indexes on the view
            for index_field in self.index_fields:
                self.session.execute('CREATE INDEX "{resource_id}_{index_field}_idx" ON "{resource_id}" ("{index_field}")'.format(
                    resource_id=resource_id,
                    index_field=index_field
                ))

        self.session.commit()

        log.info('Creating materialized view %s: SUCCESS', resource_id)


    def create(self):
        """
        Create the datastore - this action is called by the KE EMu command
        @return: None
        """
        resource_id = self.create_datastore_resource()

        source_table = self.build_source_table(resource_id)

        self.materialize_resource(resource_id, source_table)


class KeEMuSpecimensDatastore(KeEMuDatastore):

    name = 'Specimens'
    description = 'Specimen records'
    format = 'dwc'  # Darwin Core format

    package = {
        'name': u'nhm-collection',
        'notes': u'The Natural History Museum\'s collection',
        'title': "Collection",
        'extras': [{
            'key': 'spatial',
            'value': json.dumps({
                'type': 'Polygon',
                # The whole world
                'coordinates': [[[-180.0, 84.0], [180.0, 84.0], [180.0, -84.0], [-180.0, -84.0], [-180.0, 84.0]]]
            })
        }]
    }

    # Fields not to include in the _full_text index
    full_text_blacklist = [
        'modified',
        'created',
        'institutionCode',
        'dateIdentified',
        'individualCount',
        'decimalLatitude',
        'decimalLongitude',
        'verbatimLatitude',
        'verbatimLongitude',
        'minimumElevationInMeters',
        'maximumElevationInMeters',
        'higherGeography',
        'fieldNumber',
        'recordNumber',
        'eventTime',
        'minimumDepthInMeters',
        'maximumDepthInMeters',
        'year',
        'month',
        'day',
        'associatedMedia',
        'relatedResourceID',
        'relationshipOfResource',
        'higherClassification',
        'properties',
    ]

    # Extra fields to index on
    index_fields = ['scientificName']

    geom_columns = {
        'lat_field': 'decimalLatitude',
        'long_field': 'decimalLongitude'
    }

    # Fields not to include in dynamic properties
    # All fields included in DwC will be excluded automatically
    dynamic_properties_blacklist = ['ke_date_inserted', 'type', 'date_collected_from', 'date_collected_to']

    def build_source_table(self, resource_id):
        """
        Override the build_source_table()
        Because of the complexity of the queries, there are a number of views we need to build first
        @return: sqla source table
        """

        # Build the views on which the source table is built
        self.create_view('_geological_context_v', self._geological_context_view())
        self.create_view('_associated_records_v', self._associated_records_view(), VIEW)
        self.create_view('_multimedia_v', self._multimedia_view(), VIEW)
        self.create_view('_collection_date_v', self._collection_date_view())
        self.create_view('_taxonomy_v', self._taxonomy_view())
        self.create_view('_dynamic_properties_v', self._dynamic_properties_view())

        # Build the source table
        source_table = super(KeEMuSpecimensDatastore, self).build_source_table(resource_id)

        # Part fields can inherit from parent
        self.update_dependent_fields(source_table)

        return source_table

    def create_view(self, name, query, view_type=TABLE):

        # Does this object already exist?
        if self.view_exists(name):

            if view_type is VIEW:
                # If it's just a view and already exists, do nothing
                log.debug('View %s already exists: SKIPPING', name)
                return

            elif view_type is MATERIALIZED_VIEW:
                # If the mat view already exists, refresh it
                log.debug('Materialized view %s already exists: REFRESHING', name)
                self.session.execute(text('REFRESH MATERIALIZED VIEW {name}'.format(name=name)))
                return

            else:
                # Drop the table
                log.debug('Drop table %s', name)
                self.session.execute('DROP TABLE IF EXISTS {name}'.format(name=name))

        log.debug('Creating view %s', name)

        c = CreateAsSelect(name, query, view_type)
        self.session.execute(c)

        # And add a primary key for materialized and view
        if view_type is MATERIALIZED_VIEW:
            log.debug('Adding index to materialized view %s', name)
            self.session.execute(text('CREATE UNIQUE INDEX {name}_irn_idx ON {name} (irn)'.format(name=name)))
        elif view_type is TABLE:
            log.debug('Adding index to table %s', name)
            self.session.execute(text('ALTER TABLE {name} ADD PRIMARY KEY (irn)'.format(name=name)))

        log.info('Creating view %s: SUCCESS', name)

        self.session.commit()

    def datastore_query(self, force_rebuild=False):

        q = self._dwc_query()

        # Add the dynamic properties field and joins
        # Needs to go here to prevent self referential queries in _dwc_query
        _dynamic_properties_v = Table('_dynamic_properties_v', self.metadata, autoload=True)
        q = q.select_from(q.froms[0].join(_dynamic_properties_v, CatalogueModel.__table__.c.irn == _dynamic_properties_v.c.irn))
        q = q.column(_dynamic_properties_v.c.properties.label('dynamicProperties'))
        q = q.group_by(_dynamic_properties_v.c.irn)

        return q

    @staticmethod
    def get_dynamic_properties_field_name(name):
        """
        Convert a field name to capital case
        @param name: field name
        @return: FieldName
        """

        # Some fields in dynamic properties map to existing DwC fields, so we should use the old field name
        field_name_mappings = {
            'weight': 'observedWeight'
        }

        try:
            field_name = field_name_mappings[name]
        except KeyError:
            field_name = ''.join(n.capitalize() or '_' for n in name.split('_'))
            field_name = field_name[0].lower() + field_name[1:]

        return field_name

    def _columns_to_string(self, columns):
        """
        Given a list of columns, convert to select string
        @param columns:
        @return: string
        """

        cols = []

        for c in columns:

            col_str = "'{field_name}=' || "
            # For text columns, we want to remove = and ; so text can be parsed
            col_str += "translate({table}.\"{column}\", ';=', '')" if c.type.python_type is str else "{table}.\"{column}\""

            cols.append(
                col_str.format(
                    field_name=self.get_dynamic_properties_field_name(c.name),
                    table=c.table,
                    column=c.name
                )
            )

        return ', '.join(cols)

    def _dynamic_properties_view(self):

        """
        Rather than having a wide table (which CKAN is really struggling with), we can use DwC DynamicProperties
        Peter Desmet recommends this approach: https://groups.google.com/forum/#!msg/canadensys/Et6VN0nbZ18/R4-4xRQ4u20J
        Also see: http://rs.tdwg.org/dwc/terms/simple/index.htm
        @return: sqla query - irn, properties (key=value; key=value)
        """
        qs = []

        _taxonomy_v = Table('_taxonomy_v', self.metadata, autoload=True)

        for ke_model in itertools.chain([SpecimenModel], SpecimenModel.__subclasses__(), PartModel.__subclasses__()):

            if ke_model is StubModel:
                continue

            # Get all columns not mapped to dwc
            columns = self.dwc_get_dynamic_properties(ke_model)

            columns_str = self._columns_to_string(columns)

            tables = set([column.table for column in columns if column.table not in [SpecimenModel.__table__, SiteModel.__table__, CollectionEventModel.__table__, _taxonomy_v]])

            q = select([
                SpecimenModel.__table__.c.irn,
            ])

            # Build select from (for the joins)
            # We always want the CatalogueModel
            select_from = SpecimenModel.__table__.join(CatalogueModel.__table__, CatalogueModel.__table__.c.irn == SpecimenModel.__table__.c.irn)
            q = q.group_by(SpecimenModel.__table__.c.irn)
            q = q.group_by(CatalogueModel.__table__.c.irn)

            for table in tables:
                select_from = select_from.join(table, table.c.irn == SpecimenModel.__table__.c.irn)
                q = q.group_by(table.c.irn)

            # Add joins and group by to events, sites & taxonomy
            select_from = select_from.outerjoin(SiteModel.__table__, SiteModel.__table__.c.irn == SpecimenModel.__table__.c.site_irn)
            q = q.group_by(SiteModel.__table__.c.irn)

            select_from = select_from.outerjoin(CollectionEventModel.__table__, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)
            q = q.group_by(CollectionEventModel.__table__.c.irn)

            select_from = select_from.outerjoin(_taxonomy_v, _taxonomy_v.c.irn == SpecimenModel.__table__.c.irn)
            q = q.group_by(_taxonomy_v.c.irn)

            # Only select a particular type - this does mean more and a slower query - but ensures data is correct
            q = q.where(CatalogueModel.__table__.c.type == ke_model.__mapper_args__['polymorphic_identity'])

            # Add some extra fields for content types with external tables (Mineralogy, Paleo?)

            # Mineralogy - so add mineralogical ages
            if ke_model is MineralogySpecimenModel:
                select_from = select_from.outerjoin(specimen_mineralogical_age, specimen_mineralogical_age.c.mineralogy_irn == SpecimenModel.__table__.c.irn)
                select_from = select_from.outerjoin(MineralogicalAge.__table__, MineralogicalAge.__table__.c.id == specimen_mineralogical_age.c.mineralogical_age_id)
                # Append the new fields to the existing columns
                columns_str += ", string_agg(concat_ws('=', replace(age_type, ' ', ''), age), '; ')"

            elif ke_model is ParasiteCardModel:
                select_from = select_from.outerjoin(HostParasiteAssociation.__table__, HostParasiteAssociation.__table__.c.parasite_card_irn == SpecimenModel.__table__.c.irn)
                select_from = select_from.outerjoin(TaxonomyModel.__table__, TaxonomyModel.__table__.c.irn == HostParasiteAssociation.__table__.c.taxonomy_irn)
                columns_str += ", string_agg(format('%s=%s; %sStage=%s', parasite_host, taxonomy.scientific_name, parasite_host, stage), '; ')"

            elif ke_model is PalaeontologySpecimenModel:
                select_from = select_from.outerjoin(StratigraphyModel.__table__, StratigraphyModel.__table__.c.irn == PalaeontologySpecimenModel.__table__.c.stratigraphy_irn)
                q = q.group_by(StratigraphyModel.__table__.c.irn)
                columns = self.dwc_get_dynamic_properties(StratigraphyModel, False)
                columns_str += ', ' + self._columns_to_string(columns)

            # Add the main dynamic properties field (we do it here, so it can be manipulated by specific case
            q = q.column(func.concat_ws(literal_column("'; '"), literal_column(columns_str)).label('properties'))

            q = q.select_from(select_from)

            # Create list of queries we'll union_all later
            qs.append(q)

        return union_all(*qs)

    @staticmethod
    def _geological_context_view():
        """
        Create a view of DwC geological context fields
        Based on stratigraphic_unit stratigraphy_stratigraphic_unit
        """
        contexts = OrderedDict()
        contexts['earliestEonOrLowestEonothem'] = {'direction': 'from', 'stratigraphic_type': 'eon'}
        contexts['latestEonOrHighestEonothem'] = {'direction': 'to', 'stratigraphic_type': 'eon'}

        contexts['earliestEraOrLowestErathem'] = {'direction': 'from', 'stratigraphic_type': 'era'}
        contexts['latestEraOrHighestErathem'] = {'direction': 'to', 'stratigraphic_type': 'era'}

        contexts['earliestPeriodOrLowestSystem'] = {'direction': 'from', 'stratigraphic_type': 'period'}
        contexts['latestPeriodOrHighestSystem'] = {'direction': 'to', 'stratigraphic_type': 'period'}

        contexts['earliestEpochOrLowestSeries'] = {'direction': 'from', 'stratigraphic_type': 'epoch'}
        contexts['latestEpochOrHighestSeries'] = {'direction': 'to', 'stratigraphic_type': 'epoch'}

        contexts['earliestEonOrLowestEonothem'] = {'direction': 'from', 'stratigraphic_type': 'eon'}
        contexts['latestEonOrHighestEonothem'] = {'direction': 'to', 'stratigraphic_type': 'eon'}

        contexts['earliestAgeOrLowestStage'] = {'direction': 'from', 'stratigraphic_type': 'stage'}
        contexts['latestAgeOrHighestStage'] = {'direction': 'to', 'stratigraphic_type': 'stage'}

        contexts['lowestBiostratigraphicZone'] = {'direction': 'from', 'stratigraphic_type': 'zone'}
        contexts['highestBiostratigraphicZone'] = {'direction': 'to', 'stratigraphic_type': 'zone'}

        contexts['group'] = {'stratigraphic_type': 'group'}
        contexts['formation'] = {'stratigraphic_type': 'formation'}
        contexts['member'] = {'stratigraphic_type': 'member'}
        contexts['bed'] = {'stratigraphic_type': 'bed'}

        cols = [PalaeontologySpecimenModel.irn]

        for label, params in contexts.items():

            sub_q = select([
                func.array_to_string(
                    func.array_agg(
                        StratigraphicUnitModel.name
                    ), '; ')
            ])

            sub_q = sub_q.select_from(StratigraphicUnitModel.__table__.join(StratigraphicUnitAssociation.__table__, StratigraphicUnitModel.__table__.c.id == StratigraphicUnitAssociation.__table__.c.unit_id))

            sub_q = sub_q.where(literal_column('%s=%s' % (StratigraphicUnitAssociation.__table__.c.stratigraphy_irn, PalaeontologySpecimenModel.__table__.c.stratigraphy_irn)))

            for key, value in params.items():
                sub_q = sub_q.where(getattr(StratigraphicUnitAssociation, key) == value)

            cols.append(sub_q.label(label))

        q = select(cols)

        return q

    @staticmethod
    def _associated_records_view():
        """
        Union associated records, and both ends of the part / parent relationship
        """
        qs = [
            select([
                catalogue_associated_record.c.catalogue_irn.label('irn'),
                catalogue_associated_record.c.associated_irn.label('associated_irn'),
                literal_column("'associated'").label('rel_type')
            ]).distinct(),
            select([
                PartModel.__table__.c.irn.label('irn'),
                PartModel.__table__.c.parent_irn.label('associated_irn'),
                literal_column("'parent'").label('rel_type')
            ]).where(PartModel.__table__.c.parent_irn != None).distinct(),
            select([
                PartModel.__table__.c.parent_irn.label('irn'),
                PartModel.__table__.c.irn.label('associated_irn'),
                literal_column("'part'").label('rel_type')
            ]).where(PartModel.__table__.c.parent_irn != None).distinct()
        ]

        return union_all(*qs)

    @staticmethod
    def _taxonomy_view():

        q = select([
            Determination.specimen_irn.label('irn'),
            TaxonomyModel.scientific_name,
            TaxonomyModel.kingdom,
            TaxonomyModel.phylum,
            TaxonomyModel.taxonomic_class,
            TaxonomyModel.order,
            TaxonomyModel.suborder,
            TaxonomyModel.superfamily,
            TaxonomyModel.family,
            TaxonomyModel.subfamily,
            TaxonomyModel.genus,
            TaxonomyModel.subgenus,
            TaxonomyModel.species,
            TaxonomyModel.subspecies,
            TaxonomyModel.validity,
            TaxonomyModel.rank,
            TaxonomyModel.scientific_name_author,
            TaxonomyModel.scientific_name_author_year,
            TaxonomyModel.currently_accepted_name,
            func.concat_ws('; ',
                TaxonomyModel.kingdom,
                TaxonomyModel.phylum,
                TaxonomyModel.taxonomic_class,
                TaxonomyModel.order,
                TaxonomyModel.suborder,
                TaxonomyModel.superfamily,
                TaxonomyModel.family,
                TaxonomyModel.subfamily,
                TaxonomyModel.genus,
                TaxonomyModel.subgenus
            ).label('higher_classification')
        ])

        # NB: Printing the query will not show DISTINCT ON: Need to compile print q.compile(dialect=postgresql.dialect())
        q = q.distinct(Determination.specimen_irn)
        q = q.select_from(Determination.__table__.join(TaxonomyModel.__table__, TaxonomyModel.__table__.c.irn == Determination.__table__.c.taxonomy_irn))
        q = q.order_by(Determination.specimen_irn, desc(Determination.filed_as))

        return q

    @staticmethod
    def _collection_date_view():

        q = select([
            SpecimenModel.irn,
            cast(func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})'), Integer).label('from_date_year'),
            cast(func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})'), Integer).label('from_date_month'),
            cast(func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})'), Integer).label('from_date_day'),
            cast(func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})'), Integer).label('to_date_year'),
            cast(func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})'), Integer).label('to_date_month'),
            cast(func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})'), Integer).label('to_date_day')
        ])

        q = q.select_from(SpecimenModel.__table__.join(CollectionEventModel.__table__, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn))
        q = q.where(or_(CollectionEventModel.date_collected_from != None, CollectionEventModel.date_collected_to != None))

        return q

    @staticmethod
    def _multimedia_view():
        """
        Return a view of catalogue_irn, multimedia_irn filtered on mime_type == 'image'
        @return: query
        """

        q = select([
            catalogue_multimedia.c.catalogue_irn,
            catalogue_multimedia.c.multimedia_irn
        ])

        q = q.select_from(catalogue_multimedia.join(MultimediaModel.__table__, MultimediaModel.__table__.c.irn == catalogue_multimedia.c.multimedia_irn))
        q = q.where(MultimediaModel.mime_type == 'image')

        return q

    def _dwc_query(self):
        """
        Query for converting data from KE EMu into DwC record
        Only datasets with this method will show a DwC view
        """

        # Annoyingly, sqlalchemy doesn't support reflection of materialised views
        # See https://bitbucket.org/zzzeek/sqlalchemy/issue/2891/support-materialized-views-in-postgresql
        # For now, need to use either TABLE or VIEW if reflection is needed
        _geological_context_v = Table('_geological_context_v', self.metadata, autoload=True)
        _associated_records_v = Table('_associated_records_v', self.metadata, autoload=True)
        _taxonomy_v = Table('_taxonomy_v', self.metadata, autoload=True)
        _multimedia_v = Table('_multimedia_v', self.metadata, autoload=True)
        _collection_date_v = Table('_collection_date_v', self.metadata, autoload=True)

        q = select([

            # Catalogue model
            CatalogueModel.irn.label('_id'),
            CatalogueModel.ke_date_modified.label('modified'),  # dcterms:modified
            CatalogueModel.ke_date_modified.label('created'),  # This isn't actually in DwC - but I'm going to use dcterms:created
            literal_column("'Specimen'").label('basisOfRecord'),
            literal_column("'%s'::text" % INSTITUTION_CODE).label('institutionCode'),
            func.format(IDENTIFIER_PREFIX + '%s', CatalogueModel.irn).label('occurrenceID'),

            # Other numbers
            func.array_to_string(
                func.array_agg(
                    OtherNumbersModel.value
                ), ';').label('otherCatalogNumbers'),

            # Specimen model
            case(
                [(SpecimenModel.collection_department == 'Entomology', 'BMNH(E)')],
                else_=func.upper(func.substr(SpecimenModel.collection_department, 0, 4))
            ).label('collectionCode'),
            SpecimenModel.catalogue_number.label('catalogNumber'),
            SpecimenModel.type_status.label('typeStatus'),

            func.concat_ws('-',
                SpecimenModel.date_identified_day,
                SpecimenModel.date_identified_month,
                SpecimenModel.date_identified_year
            ).label('dateIdentified'),
            SpecimenModel.specimen_count.label('individualCount'),
            func.coalesce(
                SpecimenModel.preparation,
                SpecimenModel.preparation_type
            ).label('preparations'),
            SpecimenModel.identification_qualifier.label('identificationQualifier'),
            SpecimenModel.identified_by.label('identifiedBy'),

            # Sex stage
            func.array_to_string(
                func.array_agg(
                    SexStageModel.sex
                ), ';').label('sex'),
            func.array_to_string(
                func.array_agg(
                    SexStageModel.stage
                ), ';').label('lifeStage'),

            # Site model
            SiteModel.continent.label('continent'),
            SiteModel.country.label('country'),
            SiteModel.state_province.label('stateProvince'),
            SiteModel.county.label('county'),
            SiteModel.locality.label('locality'),
            SiteModel.island_group.label('islandGroup'),
            SiteModel.island.label('island'),
            SiteModel.geodetic_datum.label('geodeticDatum'),
            SiteModel.georef_method.label('georeferenceProtocol'),
            SiteModel.decimal_latitude.label('decimalLatitude'),
            SiteModel.decimal_longitude.label('decimalLongitude'),
            SiteModel.latitude.label('verbatimLatitude'),
            SiteModel.longitude.label('verbatimLongitude'),
            SiteModel.minimum_elevation_in_meters.label('minimumElevationInMeters'),
            SiteModel.maximum_elevation_in_meters.label('maximumElevationInMeters'),
            func.coalesce(
                SiteModel.river_basin,
                SiteModel.ocean,
                SiteModel.lake
            ).label('waterBody'),
            func.concat_ws('; ',
               SiteModel.continent,
               SiteModel.country,
               SiteModel.state_province,
               SiteModel.county,
               SiteModel.nearest_named_place
            ).label('higherGeography'),

            # CollectionEvent
            CollectionEventModel.collection_event_code.label('fieldNumber'),
            CollectionEventModel.collection_method.label('samplingProtocol'),
            func.coalesce(
                CollectionEventModel.collector_name,
                CollectionEventModel.expedition_name
            ).label('recordedBy'),
            CollectionEventModel.collector_number.label('recordNumber'),
            func.coalesce(
                CollectionEventModel.time_collected_from,
                CollectionEventModel.time_collected_to
            ).label('eventTime'),
            func.coalesce(
                CollectionEventModel.depth_from_metres,
                SiteModel.minimum_depth_in_meters
            ).label('minimumDepthInMeters'),
            func.coalesce(
                CollectionEventModel.depth_to_metres,
                SiteModel.maximum_depth_in_meters
            ).label('maximumDepthInMeters'),
            # Collection date
            func.coalesce(
                _collection_date_v.c.from_date_year,
                _collection_date_v.c.to_date_year
            ).label('year'),
            func.coalesce(
                _collection_date_v.c.from_date_month,
                _collection_date_v.c.to_date_month
            ).label('month'),
            func.coalesce(
                _collection_date_v.c.from_date_day,
                _collection_date_v.c.to_date_day
            ).label('day'),
            # Botany model
            BotanySpecimenModel.habitat_verbatim.label('habitat'),

            # Multimedia
            func.array_to_string(
                func.array_remove(
                    func.array_agg(
                        func.format(MULTIMEDIA_URL, _multimedia_v.c.multimedia_irn)
                    ),
                MULTIMEDIA_URL % ''
                ), ';').label('associatedMedia'),

            # AssociatedRecords
            func.array_to_string(
                func.array_agg(
                    _associated_records_v.c.associated_irn
                )
            , ';').label('relatedResourceID'),

            func.array_to_string(
                func.array_agg(
                    _associated_records_v.c.rel_type
                )
            , ';').label('relationshipOfResource'),

            # Geological context
            _geological_context_v.c.earliestEonOrLowestEonothem,
            _geological_context_v.c.latestEonOrHighestEonothem,
            _geological_context_v.c.earliestEraOrLowestErathem,
            _geological_context_v.c.latestEraOrHighestErathem,
            _geological_context_v.c.earliestPeriodOrLowestSystem,
            _geological_context_v.c.latestPeriodOrHighestSystem,
            _geological_context_v.c.earliestEpochOrLowestSeries,
            _geological_context_v.c.latestEpochOrHighestSeries,
            _geological_context_v.c.earliestAgeOrLowestStage,
            _geological_context_v.c.latestAgeOrHighestStage,
            _geological_context_v.c.lowestBiostratigraphicZone,
            _geological_context_v.c.highestBiostratigraphicZone,
            _geological_context_v.c.group,
            _geological_context_v.c.formation,
            _geological_context_v.c.member,
            _geological_context_v.c.bed,

            # Taxonomy
            _taxonomy_v.c.scientific_name.label('scientificName'),
            _taxonomy_v.c.kingdom.label('kingdom'),
            _taxonomy_v.c.phylum.label('phylum'),
            _taxonomy_v.c.taxonomic_class.label('class'),
            _taxonomy_v.c.order.label('order'),
            _taxonomy_v.c.family.label('family'),
            _taxonomy_v.c.genus.label('genus'),
            _taxonomy_v.c.subgenus.label('subgenus'),
            _taxonomy_v.c.species.label('specificEpithet'),
            _taxonomy_v.c.subspecies.label('infraspecificEpithet'),
            _taxonomy_v.c.rank.label('taxonRank'),

            func.concat_ws(' ',
               _taxonomy_v.c.scientific_name_author,
               _taxonomy_v.c.scientific_name_author_year
            ).label('scientificNameAuthorship'),

            _taxonomy_v.c.higher_classification.label('higherClassification')

        ])

        # Add inner join to specimen
        select_from = CatalogueModel.__table__.join(SpecimenModel.__table__, CatalogueModel.__table__.c.irn == SpecimenModel.__table__.c.irn)

        #  Add outer joins to sites, collection events etc.,
        select_from = select_from.outerjoin(SiteModel.__table__, SiteModel.__table__.c.irn == SpecimenModel.__table__.c.site_irn)
        select_from = select_from.outerjoin(CollectionEventModel.__table__, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)

        # Botany is the only model with a DwC field
        select_from = select_from.outerjoin(BotanySpecimenModel.__table__, BotanySpecimenModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)

        # Other numbers
        select_from = select_from.outerjoin(OtherNumbersModel.__table__, OtherNumbersModel.__table__.c.irn == SpecimenModel.__table__.c.irn)

        # Sex stage
        select_from = select_from.outerjoin(specimen_sex_stage, specimen_sex_stage.c.specimen_irn == CatalogueModel.__table__.c.irn)
        select_from = select_from.outerjoin(SexStageModel.__table__, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)

        # Multimedia
        select_from = select_from.outerjoin(_multimedia_v, _multimedia_v.c.catalogue_irn == SpecimenModel.__table__.c.irn)

        # Associated records
        select_from = select_from.outerjoin(_associated_records_v, _associated_records_v.c.irn == SpecimenModel.__table__.c.irn)

        # Determination
        select_from = select_from.outerjoin(_taxonomy_v, _taxonomy_v.c.irn == SpecimenModel.__table__.c.irn)

        # Geological context
        select_from = select_from.outerjoin(_geological_context_v, _geological_context_v.c.irn == SpecimenModel.__table__.c.irn)

       # Collection date context
        select_from = select_from.outerjoin(_collection_date_v, _collection_date_v.c.irn == SpecimenModel.__table__.c.irn)

        q = q.select_from(select_from)

        # Add group by clauses so my aggregates work
        q = q.group_by(CatalogueModel.__table__.c.irn)
        q = q.group_by(SpecimenModel.__table__.c.irn)
        q = q.group_by(SiteModel.__table__.c.irn)
        q = q.group_by(CollectionEventModel.__table__.c.irn)
        q = q.group_by(BotanySpecimenModel.__table__.c.irn)
        q = q.group_by(_geological_context_v.c.irn)
        q = q.group_by(_taxonomy_v.c.irn)
        q = q.group_by(_collection_date_v.c.irn)

        q = q.where(CatalogueModel.type != 'stub')

        return q

    def dwc_get_mapped_fields(self):
        """
        Return a list of all fields used in the DwC query
        """

        dwc_q = self._dwc_query()
        columns = []

        for column in dwc_q._raw_columns:

            try:
                if isinstance(column._element, Column):
                    columns.append(column._element)
                else:

                    # Get child columns (in func.* statements)
                    for child in column._element.clause_expr.get_children():
                        for clause in child.clauses:
                            if isinstance(clause, Column):
                                columns.append(clause)

            except AttributeError:
                # If we do not know the column._element, this is a complex Column - eg Case
                # These will be added manually
                pass

        # Need to add SpecimenModel.collection_department by hand, as it's in a case
        columns.append(SpecimenModel.collection_department)

        return columns

    def dwc_get_dynamic_properties(self, model, expand=True):
        """
        For a model, get all unmapped DwC fields to use as dynamicProperties
        @param model:
        @param expand: Expand to include all related models
        @return:
        """
        _taxonomy_v = Table('_taxonomy_v', self.metadata, autoload=True)
        field_mappings = self.dwc_get_mapped_fields()

        # Filter out DwC fields / IRN / Foreign Keys
        def _field_filter(field):

            if field in field_mappings:
                return False

            if 'irn' in field.key:
                return False

            # Fields we don't want to include
            if field.key in self.dynamic_properties_blacklist:
                return False

            if field.key.startswith('_'):
                return False

            return True

        # Should we get use all the tables?
        if expand:

            # Get all tables in this model (all have Site, Collection Event & Taxonomy)
            tables = set([SiteModel.__table__, CollectionEventModel.__table__, _taxonomy_v])

            for cls in inspect.getmro(model):

                try:
                    tables.add(cls.__table__)
                except AttributeError:
                    # For tertiary objects, there will be no defined __table__
                    pass

        #  Or just the one passed in
        else:

            tables = set([model.__table__])


        return list(itertools.ifilter(_field_filter, itertools.chain.from_iterable([t.columns for t in tables])))

    def update_dependent_fields(self, source_table):
        """
        Fields that inherit from parts, updates to use the parent record field value if is null
        But there are (apparently - TBC) some fields in the main specimen record that also are inheritable
        @param source_table:
        @return: None
        """

        log.debug('Updating dependent fields')

        # List of inherited fields
        dependent_fields = [
            # Taxonomy
            'scientificName',
            'kingdom',
            'phylum',
            'class',
            'order',
            'family',
            'genus',
            'subgenus',
            'specificEpithet',
            'infraspecificEpithet',
            'taxonRank',
            'scientificNameAuthorship',
            'higherClassification',
            # Site
            'continent',
            'country',
            'stateProvince',
            'county',
            'locality',
            'islandGroup',
            'island',
            'geodeticDatum',
            'georeferenceProtocol',
            'decimalLatitude',
            'decimalLongitude',
            'verbatimLatitude',
            'verbatimLongitude',
            'minimumElevationInMeters',
            'maximumElevationInMeters',
            'waterBody',
            'higherGeography',
            # Collection event
            'fieldNumber',
            'samplingProtocol',
            'recordedBy',
            'recordNumber',
            'eventTime',
            'minimumDepthInMeters',
            'maximumDepthInMeters',
            'year',
            'month',
            'day',
            'habitat',
        ]

        # There's no way of doing update set from in sqlalchemy - so add it just as plain sql
        values = []
        for dependent_field in dependent_fields:
            values.append('"{inherited_field}" = COALESCE(s1."{inherited_field}", s2."{inherited_field}") '.format(inherited_field=dependent_field))

        sql = """
              UPDATE "{table}" s1
              SET {values}
              FROM "{table}" s2
                INNER JOIN {part} p ON p.parent_irn = s2._id
              WHERE s1._id = p.irn
              """.format(table=source_table,
                         values=', '.join(values),
                         part=PartModel.__table__)

        self.session.execute(sql)

        log.info('Updating dependent fields: SUCCESS')


class KeEMuIndexlotDatastore(KeEMuDatastore):
    """
    KE EMu artefacts datastore
    """
    name = 'Index lots'
    description = 'Entomology indexlot records'
    package = KeEMuSpecimensDatastore.package

    def datastore_query(self):

        # Create material_t type if it doesn't exist
        # We do not want to drop and recreate, as table/view will be dependent upon this
        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'material_t\')').scalar():

            self.session.execute(
                """
                CREATE TYPE material_t
                AS (count int, sex text, types text, stage text, primary_type_number text)
                """
            )

        q = select([
            IndexLotModel.irn.label('_id'),
            IndexLotModel.material,
            IndexLotModel.is_type,
            IndexLotModel.media,
            IndexLotModel.kind_of_material,
            IndexLotModel.kind_of_media,
            TaxonomyModel.scientific_name,
            TaxonomyModel.kingdom,
            TaxonomyModel.phylum,
            TaxonomyModel.taxonomic_class,
            TaxonomyModel.order,
            TaxonomyModel.suborder,
            TaxonomyModel.superfamily,
            TaxonomyModel.family,
            TaxonomyModel.subfamily,
            TaxonomyModel.genus,
            TaxonomyModel.subgenus,
            TaxonomyModel.species,
            TaxonomyModel.subspecies,
            TaxonomyModel.validity,
            TaxonomyModel.rank.label('taxonomic_rank'),
            TaxonomyModel.scientific_name_author,
            TaxonomyModel.scientific_name_author_year,
            TaxonomyModel.currently_accepted_name,
            # Material detail
            func.array_to_json(
                func.array_agg(
                    func.row_to_json(
                        literal_column('ROW(count, sex, types, stage, primary_type_number)::material_t')
                    )
                )
            ).label('material_detail'),

            # Multimedia
            func.array_to_string(
                func.array_remove(
                    func.array_agg(
                        func.format(MULTIMEDIA_URL, catalogue_multimedia.c.multimedia_irn)
                    ),
                MULTIMEDIA_URL % ''
                ), ';').label('multimedia'),

            # Extra index so the material is represented
            func.array_to_string(
                func.array_agg(
                    func.concat_ws(' ',
                        IndexLotMaterialModel.stage,
                        IndexLotMaterialModel.sex,
                        IndexLotMaterialModel.types
                    )
                ), ' ').label('_index'),
        ])

        # Material
        select_from = IndexLotModel.__table__.outerjoin(TaxonomyModel.__table__, TaxonomyModel.__table__.c.irn == IndexLotModel.__table__.c.taxonomy_irn)
        # Taxonomy
        select_from = select_from.outerjoin(IndexLotMaterialModel.__table__, IndexLotModel.__table__.c.irn == IndexLotMaterialModel.__table__.c.irn)
        # Multimedia
        select_from = select_from.outerjoin(catalogue_multimedia, catalogue_multimedia.c.catalogue_irn == IndexLotModel.__table__.c.irn)
        q = q.select_from(select_from)

        q = q.group_by(IndexLotModel.__table__.c.irn)
        q = q.group_by(TaxonomyModel.__table__.c.irn)

        return q

class KeEMuArtefactDatastore(KeEMuDatastore):
    """
    KE EMu artefacts datastore
    """
    name = 'Artefacts'
    description = 'Artefacts'
    package = {
        'name': u'nhm-artefacts',
        'notes': u'Artefacts from The Natural History Museum',
        'title': "Artefacts"
    }

    full_text_blacklist = ['multimedia']

    def datastore_query(self):

        q = select([
            ArtefactModel.irn.label('_id'),
            ArtefactModel.kind,
            ArtefactModel.name,
            func.array_to_string(
                func.array_remove(
                    func.array_agg(
                        func.format(MULTIMEDIA_URL, catalogue_multimedia.c.multimedia_irn)
                    ),
                MULTIMEDIA_URL % ''
                ), '; ').label('multimedia'),

        ])

        q = q.select_from(ArtefactModel.__table__.join(catalogue_multimedia, catalogue_multimedia.c.catalogue_irn == ArtefactModel.__table__.c.irn))

        # Add group by clauses so my aggregates work
        q = q.group_by(ArtefactModel.__table__.c.irn)
        return q