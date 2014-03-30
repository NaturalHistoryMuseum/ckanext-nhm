#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""
import sys
from ke2sql.model.keemu import *

from ke2sql.model.keemu import specimen_sex_stage, catalogue_associated_record, catalogue_multimedia, specimen_mineralogical_age
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, column_property
from sqlalchemy.sql.expression import select, join
from sqlalchemy.sql import expression, functions
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import text
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Boolean, Date, UniqueConstraint, Enum, DateTime, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast
from sqlalchemy import literal_column
from sqlalchemy import case
from sqlalchemy import and_, or_
from ckanext.nhm.lib.db import get_datastore_session, CreateAsSelect
import csv
import sqlalchemy
import itertools
import abc
import ckan.model as model
import ckan.logic as logic
from itertools import chain
from sqlalchemy import union_all
import inspect
from collections import OrderedDict
from sqlalchemy.schema import MetaData
from sqlalchemy import desc
from sqlalchemy import update

MULTIMEDIA_URL = 'http://www.nhm.ac.uk/emu-classes/class.EMuMedia.php?irn=%s'

VIEW = 'VIEW'
MATERIALIZED_VIEW = 'MATERIALIZED VIEW'
TABLE = 'TABLE'

Base = declarative_base()

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
    index_field_blacklist = []

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
        params = dict(chain(self.default_package_params.iteritems(), self.package.iteritems()))

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

        print 'Creating datastore %s' % self.name

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

        print 'Creating datastore %s: SUCCESS' % resource_id

        return resource_id

    def build_source_table(self, resource_id, rebuild=True):
        """
        Build a table to use as a source for the materialised view

        @param resource_id: CKAN UUID for the dataset resource
        @return: SQLA object representing the source table
        """
        source_table_name = '_source_%s' % resource_id

        datastore_query = self.datastore_query()

        try:
            source_table = Table(source_table_name, self.metadata, autoload=True)

            # If exists, do we want to rebuild (only really used for debugging)
            if rebuild:

                # Source table exists
                # Remove existing data
                self.session.execute(text('TRUNCATE TABLE "{source_table_name}"'.format(source_table_name=source_table_name)))

                # Ensure columns match
                assert [c.key for c in datastore_query.c] == [c.key for c in source_table.c]

                # INSERT INTO source_table (columns) (datastore_query)
                q = source_table.insert().from_select(source_table.c, datastore_query)
                self.session.execute(q)

                print 'Updating source table: SUCCESS'

        except NoSuchTableError:

            # If table doesn't exist create it
            q = CreateAsSelect(source_table_name, datastore_query)
            self.session.execute(q)
            self.session.commit()

            # Reflect the new source table
            source_table = Table(source_table_name, self.metadata, autoload=True)

            print 'Creating source table: SUCCESS'

        return source_table

    def get_index_fields(self, source_table):
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

        if self.index_field_blacklist:
            q = q.where(information_schema.c.column_name.notin_(self.index_field_blacklist))

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
        index_fields = self.get_index_fields(source_table)

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
                    literal_column("ARRAY_TO_STRING(ARRAY[%s], ' ')" % index_fields)
                ).label('_full_text')
            )

            # Create the view
            self.session.execute('CREATE MATERIALIZED VIEW "{resource_id}" AS ({view_q})'.format(resource_id=resource_id, view_q=view_q))
            # Create index on the view
            self.session.execute('CREATE UNIQUE INDEX "{resource_id}_idx" ON "{resource_id}" (_id)'.format(resource_id=resource_id))

            # TODO: Add other indexes? Scientific name?

        self.session.commit()

        print 'Created datastore %s: SUCCESS' % self.name

    def create(self):
        """
        Create the datastore - this action is called by the KE EMu command
        @return: None
        """
        resource_id = self.create_datastore_resource()

        # source_table = self.build_source_table(resource_id)

        # self.materialize_resource(resource_id, source_table)


class KeEMuSpecimensDatastore(KeEMuDatastore):

    # TODO: Check all data and fields
    # TODO: Add more to dynamic properties (sites etc.,)

    name = 'Specimens'
    description = 'Specimen records'
    format = 'dwc'  # Darwin Core format

    package = {
        'name': u'nhm-collection32',
        'notes': u'The Natural History Museum\'s collection',
        'title': "Collection"
    }

    index_field_blacklist = [
        'associatedMedia',
        'AssociatedRecords',
        'DecimalLatitude',
        'verbatimLatitude',
        'verbatimLongitude',
        'MinimumElevationInMeters',
        'MaximumElevationInMeters',
        'FieldNumber',
        'CollectorNumber',
        'DecimalLongitude',
        'properties',
        'StartTimeOfDay',
        'EndTimeOfDay',
        'InstitutionCode',
        'date_collected_from',
        'date_collected_to',
        'HigherTaxon',
        'ScientificNameAuthorYear',
        'CollectedFromYear',
        'CollectedFromMonth',
        'CollectedFromMonth',
        'CollectedToYear',
        'CollectedToMonth',
        'CollectedToDay',
        'CollectedYear',
        'CollectedMonth',
        'CollectedDay'
    ]

    def build_source_table(self, resource_id, rebuild=False):
        """
        Override the build_source_table()
        Because of the complexity of the queries, there are a number of views we need to build first
        @return: sqla source table
        """

        if rebuild:

            # Build the views on which the source table is built
            self.create_view('_geological_context_v', self._geological_context_view())
            self.create_view('_associated_records_v', self._associated_records_view(), VIEW)
            self.create_view('_collection_date_v', self._collection_date_view())
            self.create_view('_taxonomy_v', self._taxonomy_view())
            self.create_view('_dynamic_properties_v', self._dynamic_properties_view())

        # Build the source table
        source_table = super(KeEMuSpecimensDatastore, self).build_source_table(resource_id, rebuild)

        # Part fields can inherit from parent
        self.update_inherited_fields(source_table)

        return source_table

    def create_view(self, name, query, view_type=TABLE):

        # Does this object already exist?
        if self.view_exists(name):

            if view_type is VIEW:
                # If it's just a view and already exists, do nothing
                print 'View %s already exists: SKIPPING' % name
                return

            elif view_type is MATERIALIZED_VIEW:
                # If the mat view already exists, refresh it
                print 'Materialized view %s already exists: REFRESHING' % name
                self.session.execute(text('REFRESH MATERIALIZED VIEW {name}'.format(name=name)))
                return

            else:
                # Drop the table
                print 'Drop table %s' % name
                self.session.execute('DROP TABLE IF EXISTS {name}'.format(name=name))

        print 'Creating view %s' % name

        c = CreateAsSelect(name, query, view_type)
        self.session.execute(c)

        # And add a primary key for materialized and view
        if view_type is MATERIALIZED_VIEW:
            print 'Adding index to materialized view %s' % name
            self.session.execute(text('CREATE UNIQUE INDEX {name}_irn_idx ON {name} (irn)'.format(name=name)))
        elif view_type is TABLE:
            print 'Adding index to table %s' % name
            self.session.execute(text('ALTER TABLE {name} ADD PRIMARY KEY (irn)'.format(name=name)))

        print 'Creating view %s: SUCCESS' % name

        self.session.commit()

    def datastore_query(self, force_rebuild=False):

        q = self._dwc_query()

        # Add the dynamic properties field and joins
        # Needs to go here to prevent self referential queries in _dwc_query
        metadata = MetaData(self.session.bind)
        _dynamic_properties_v = Table('_dynamic_properties_v', metadata, autoload=True)
        q = q.select_from(q.froms[0].join(_dynamic_properties_v, CatalogueModel.__table__.c.irn == _dynamic_properties_v.c.irn))
        q = q.column(_dynamic_properties_v.c.properties.label('DynamicProperties'))
        q = q.group_by(_dynamic_properties_v.c.irn)

        return q

    @staticmethod
    def convert_field_name(name):
        """
        Convert a field name to capital case
        @param name: field name
        @return: FieldName
        """
        return ''.join(n.capitalize() or '_' for n in name.split('_'))

    def _dynamic_properties_view(self):

        """
        Rather than having a wide table (which CKAN is really struggling with), we can use DwC DynamicProperties
        Peter Desmet recommends this approach: https://groups.google.com/forum/#!msg/canadensys/Et6VN0nbZ18/R4-4xRQ4u20J
        @return: sqla query - irn, properties (key=value; key=value)
        """
        qs = []

        for ke_model in itertools.chain([SpecimenModel], SpecimenModel.__subclasses__(), PartModel.__subclasses__()):

            if ke_model is StubModel:
                continue

            # Get all columns not mapped to dwc
            columns = self.dwc_get_unmapped_fields(ke_model)

            cols = ', '.join("'%s=' || %s.%s" % (self.convert_field_name(c.name), c.table, c.name) for c in columns)

            # if ke_model is MineralogySpecimenModel:
            #     cols += ", string_agg(concat_ws('=', replace(age_type, ' ', ''), age), '; ')"

            tables = set([column.table for column in columns if column.table not in [SpecimenModel.__table__, SiteModel.__table__, CollectionEventModel.__table__]])

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

            # Add joins and group by to events and sites
            select_from = select_from.outerjoin(SiteModel, SiteModel.__table__.c.irn == SpecimenModel.__table__.c.site_irn)
            q = q.group_by(SiteModel.__table__.c.irn)

            select_from = select_from.outerjoin(CollectionEventModel, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)
            q = q.group_by(CollectionEventModel.__table__.c.irn)



            # TODO: Temp - put back
            # Only select a particular type - this does mean more and a slower query - but ensures data is correct
            # q = q.where(CatalogueModel.__table__.c.type == ke_model.__mapper_args__['polymorphic_identity'])

            # Add some extra fields for content types with external tables (Mineralogy, Paleo?)

            # Mineralogy - so add mineralogical ages
            if ke_model is MineralogySpecimenModel:
                select_from = select_from.outerjoin(specimen_mineralogical_age, specimen_mineralogical_age.c.mineralogy_irn == SpecimenModel.__table__.c.irn)
                select_from = select_from.outerjoin(MineralogicalAge, MineralogicalAge.__table__.c.id == specimen_mineralogical_age.c.mineralogical_age_id)
                # Append the new fields to the existing columns
                cols += ", string_agg(concat_ws('=', replace(age_type, ' ', ''), age), '; ')"


            # Add the main dynamic properties field (we do it here, so it can be manipulated by specific case
            q = q.column(func.concat_ws(literal_column("'; '"), literal_column(cols)).label('properties'))

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
        contexts['earliestEraOrLowestErathem'] = {'direction': 'to', 'stratigraphic_type': 'era'}

        contexts['earliestPeriodOrLowestSystem'] = {'direction': 'from', 'stratigraphic_type': 'period'}
        contexts['latestPeriodOrHighestSystem'] = {'direction': 'to', 'stratigraphic_type': 'period'}

        contexts['earliestEpochOrLowestSeries'] = {'direction': 'from', 'stratigraphic_type': 'epoch'}
        contexts['latestEpochOrHighestSeries'] = {'direction': 'to', 'stratigraphic_type': 'epoch'}

        contexts['earliestEonOrLowestEonothem'] = {'direction': 'from', 'stratigraphic_type': 'eon'}
        contexts['latestEonOrHighestEonothem'] = {'direction': 'to', 'stratigraphic_type': 'eon'}

        contexts['earliestAgeOrLowestStage'] = {'direction': 'from', 'stratigraphic_type': 'stage'}
        contexts['latestAgeOrHighestStage'] = {'direction': 'to', 'stratigraphic_type': 'stage'}

        # TODO: There are other zones
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
                catalogue_associated_record.c.associated_irn.label('associated_irn')
            ]).distinct(),
            select([
                PartModel.__table__.c.irn.label('irn'),
                PartModel.__table__.c.parent_irn.label('associated_irn'),
            ]).where(PartModel.__table__.c.parent_irn != None).distinct(),
            select([
                PartModel.__table__.c.parent_irn.label('irn'),
                PartModel.__table__.c.irn.label('associated_irn'),
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
            TaxonomyModel.family,
            TaxonomyModel.subfamily,
            TaxonomyModel.genus,
            TaxonomyModel.subgenus,
            TaxonomyModel.species,
            TaxonomyModel.subspecies,
            TaxonomyModel.rank,
            TaxonomyModel.scientific_name_author,
            TaxonomyModel.scientific_name_author_year,
            func.concat_ws('; ',
                TaxonomyModel.kingdom,
                TaxonomyModel.phylum,
                TaxonomyModel.order,
                TaxonomyModel.suborder,
                TaxonomyModel.superfamily,
                TaxonomyModel.family,
                TaxonomyModel.subfamily,
                TaxonomyModel.genus,
                TaxonomyModel.subgenus
            ).label('HigherTaxon')
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
            func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})').label('from_date_year'),
            func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})').label('from_date_month'),
            func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})').label('from_date_day'),
            func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})').label('to_date_year'),
            func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})').label('to_date_month'),
            func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})').label('to_date_day')
        ])

        q = q.select_from(SpecimenModel.__table__.join(CollectionEventModel.__table__, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn))
        q = q.where(or_(CollectionEventModel.date_collected_from != None, CollectionEventModel.date_collected_to != None))

        return q

    def _dwc_query(self):
        """
        Query for converting data from KE EMu into DwC record
        Only datasets with this method will show a DwC view
        """

        INSTITUTION_CODE = 'NHMUK'
        IDENTIFIER_PREFIX = '%s:ecatalogue:' % INSTITUTION_CODE

        # Reflected views
        metadata = MetaData(self.session.bind)
        # Annoyingly, sqlalchemy doesn't support reflection of materialised views
        # See https://bitbucket.org/zzzeek/sqlalchemy/issue/2891/support-materialized-views-in-postgresql
        # For now, need to use either TABLE or VIEW if reflection is needed
        _geological_context_v = Table('_geological_context_v', metadata, autoload=True)
        _associated_records_v = Table('_associated_records_v', metadata, autoload=True)
        _taxonomy_v = Table('_taxonomy_v', metadata, autoload=True)
        _collection_date_v = Table('_collection_date_v', metadata, autoload=True)

        q = select([

            # Catalogue model
            CatalogueModel.irn.label('_id'),
            CatalogueModel.ke_date_modified.label('modified'),
            literal_column("'%s'::text" % INSTITUTION_CODE).label('InstitutionCode'),
            func.format(IDENTIFIER_PREFIX + '%s', CatalogueModel.irn).label('CatalogueNumber'),

            # Other numbers
            func.array_to_string(
                func.array_agg(
                    OtherNumbersModel.value
                ), ';').label('OtherNumbers'),

            # Specimen model
            case(
                [(SpecimenModel.collection_department == 'Entomology', 'BMNH(E)')],
                else_=func.upper(func.substr(SpecimenModel.collection_department, 0, 4))
            ).label('CollectionCode'),
            SpecimenModel.catalogue_number.label('CatalogNumber'),
            SpecimenModel.type_status.label('TypeStatus'),
            SpecimenModel.date_identified_day.label('DayIdentified'),
            SpecimenModel.date_identified_month.label('MonthIdentified'),
            SpecimenModel.date_identified_year.label('YearIdentified'),
            SpecimenModel.specimen_count.label('IndividualCount'),
            SpecimenModel.preparation.label('Preparations'),
            SpecimenModel.preparation_type.label('PreparationType'),
            SpecimenModel.weight.label('ObservedWeight'),
            SpecimenModel.identification_qualifier.label('IdentificationQualifier'),
            SpecimenModel.identified_by.label('IdentifiedBy'),

            # Sex stage
            func.array_to_string(
                func.array_agg(
                    SexStageModel.sex
                ), ';').label('Sex'),
            func.array_to_string(
                func.array_agg(
                    SexStageModel.stage
                ), ';').label('LifeStage'),

            # Site model
            SiteModel.continent.label('Continent'),
            SiteModel.country.label('Country'),
            SiteModel.state_province.label('StateProvince'),
            SiteModel.county.label('County'),
            SiteModel.locality.label('Locality'),
            SiteModel.ocean.label('ContinentOcean'),
            SiteModel.island_group.label('IslandGroup'),
            SiteModel.island.label('Island'),
            SiteModel.geodetic_datum.label('GeodeticDatum'),
            SiteModel.georef_method.label('GeorefMethod'),
            SiteModel.decimal_latitude.label('DecimalLatitude'),
            SiteModel.decimal_longitude.label('DecimalLongitude'),
            SiteModel.latitude.label('verbatimLatitude'),
            SiteModel.longitude.label('verbatimLongitude'),
            SiteModel.minimum_elevation_in_meters.label('MinimumElevationInMeters'),
            SiteModel.maximum_elevation_in_meters.label('MaximumElevationInMeters'),
            func.coalesce(
                SiteModel.river_basin,
                SiteModel.ocean,
                SiteModel.lake
            ).label('WaterBody'),
            func.concat_ws('; ',
               SiteModel.continent,
               SiteModel.country,
               SiteModel.state_province,
               SiteModel.county,
               SiteModel.nearest_named_place
            ).label('HigherGeography'),

            # CollectionEvent
            CollectionEventModel.time_collected_from.label('StartTimeOfDay'),
            CollectionEventModel.time_collected_to.label('EndTimeOfDay'),
            CollectionEventModel.collection_event_code.label('FieldNumber'),
            CollectionEventModel.collection_method.label('samplingProtocol'),
            func.coalesce(
                CollectionEventModel.collector_name,
                CollectionEventModel.expedition_name
            ).label('Collector'),
            CollectionEventModel.collector_number.label('CollectorNumber'),
            func.coalesce(
                CollectionEventModel.time_collected_from,
                CollectionEventModel.time_collected_to
            ).label('TimeOfDay'),
            func.coalesce(
                CollectionEventModel.depth_from_metres,
                SiteModel.minimum_depth_in_meters
            ).label('minimumDepthInMeters'),
            func.coalesce(
                CollectionEventModel.depth_to_metres,
                SiteModel.maximum_depth_in_meters
            ).label('maximumDepthInMeters'),
            # Collection date
            _collection_date_v.c.from_date_year.label('CollectedFromYear'),
            _collection_date_v.c.from_date_month.label('CollectedFromMonth'),
            _collection_date_v.c.from_date_day.label('CollectedFromDay'),
            _collection_date_v.c.to_date_year.label('CollectedToYear'),
            _collection_date_v.c.to_date_year.label('CollectedToMonth'),
            _collection_date_v.c.to_date_day.label('CollectedToDay'),
            func.coalesce(
                _collection_date_v.c.from_date_year,
                _collection_date_v.c.to_date_year
            ).label('CollectedYear'),
            func.coalesce(
                _collection_date_v.c.from_date_month,
                _collection_date_v.c.to_date_month
            ).label('CollectedMonth'),
            func.coalesce(
                _collection_date_v.c.from_date_day,
                _collection_date_v.c.to_date_day
            ).label('CollectedDay'),
            # Botany model
            BotanySpecimenModel.habitat_verbatim.label('Habitat'),

            # Multimedia
            func.array_to_string(
                func.array_remove(
                    func.array_agg(
                        func.format(MULTIMEDIA_URL, catalogue_multimedia.c.multimedia_irn)
                    ),
                MULTIMEDIA_URL % ''
                ), ';').label('associatedMedia'),

            # AssociatedRecords
            func.array_to_string(
                func.array_agg(
                    _associated_records_v.c.associated_irn
                )
            , ';').label('AssociatedRecords'),

            # Geological context
            _geological_context_v.c.earliestEonOrLowestEonothem,
            _geological_context_v.c.latestEonOrHighestEonothem,
            _geological_context_v.c.earliestEraOrLowestErathem,
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

            # Taxonomy
            _taxonomy_v.c.scientific_name.label('ScientificName'),
            _taxonomy_v.c.kingdom.label('Kingdom'),
            _taxonomy_v.c.phylum.label('Phylum'),
            _taxonomy_v.c.taxonomic_class.label('Class'),
            _taxonomy_v.c.order.label('Order'),
            _taxonomy_v.c.suborder.label('Suborder'),
            _taxonomy_v.c.family.label('Family'),
            _taxonomy_v.c.subfamily.label('Subfamily'),
            _taxonomy_v.c.genus.label('Genus'),
            _taxonomy_v.c.subgenus.label('Subgenus'),
            _taxonomy_v.c.species.label('Species'),
            _taxonomy_v.c.subspecies.label('Subspecies'),
            _taxonomy_v.c.rank.label('Rank'),
            _taxonomy_v.c.scientific_name_author.label('ScientificNameAuthor'),
            _taxonomy_v.c.scientific_name_author_year.label('ScientificNameAuthorYear'),
            _taxonomy_v.c.HigherTaxon

        ])

        # Add inner join to specimen
        select_from = CatalogueModel.__table__.join(SpecimenModel.__table__, CatalogueModel.__table__.c.irn == SpecimenModel.__table__.c.irn)

        #  Add outer joins to sites, collection events etc.,
        select_from = select_from.outerjoin(SiteModel.__table__, SiteModel.__table__.c.irn == SpecimenModel.__table__.c.site_irn)
        select_from = select_from.outerjoin(CollectionEventModel.__table__, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)

        # Botany is the only model with a DwC field
        select_from = select_from.outerjoin(BotanySpecimenModel.__table__, BotanySpecimenModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)

        # Other numbers
        select_from = select_from.outerjoin(OtherNumbersModel, OtherNumbersModel.__table__.c.irn == SpecimenModel.__table__.c.irn)

        # Sex stage
        select_from = select_from.outerjoin(specimen_sex_stage, specimen_sex_stage.c.specimen_irn == CatalogueModel.__table__.c.irn)
        select_from = select_from.outerjoin(SexStageModel.__table__, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)

        # Multimedia
        select_from = select_from.outerjoin(catalogue_multimedia, catalogue_multimedia.c.catalogue_irn == SpecimenModel.__table__.c.irn)

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

    def dwc_get_unmapped_fields(self, model):
        """
        For a model, get all unmapped DwC fields
        """

        field_mappings = self.dwc_get_mapped_fields()

        # Filter out DwC fields / IRN / Foreign Keys
        def _field_filter(field):

            if field in field_mappings:
                return False

            if 'irn' in field.key:
                return False

            # Fields we don't want to include
            if field.key in ['ke_date_inserted', 'type']:
                return False

            if field.key.startswith('_'):
                return False

            return True

        # Get all tables in this model (all have SIte & Collection Event)
        tables = set([SiteModel.__table__, CollectionEventModel.__table__])

        for cls in inspect.getmro(model):

            try:
                tables.add(cls.__table__)
            except AttributeError:
                # For tertiary objects, there will be no defined __table__
                pass

        return list(itertools.ifilter(_field_filter, itertools.chain.from_iterable([t.columns for t in tables])))

    # def def_list_all_unmapped(self):
    #     """
    #     Output a list of all unmapped fields
    #     """
    #     unmapped_fields = OrderedDict()
    #
    #     for model in itertools.chain([SpecimenModel], SpecimenModel.__subclasses__(), PartModel.__subclasses__()):
    #
    #         for field in self.dwc_get_unmapped_fields(model):
    #
    #             try:
    #
    #                 if model.__table__.name not in unmapped_fields[field.name]:
    #                     unmapped_fields[field.name].append(model.__table__.name)
    #
    #             except KeyError:
    #                 unmapped_fields[field.name] = [model.__table__.name]
    #
    #     for unmapped_field, models in unmapped_fields.items():
    #         print '%s\t%s' % (unmapped_field, ';'.join(models))

    def update_inherited_fields(self, source_table):
        """
        Fields that inherit from parts, updates to use the parent record field value if is null
        But there are (apparently - TBC) some fields in the main specimen record that also are inheritable
        @param source_table:
        @return: None
        """

        print 'Updating dependent fields'

        # List of inherited fields
        inherited_fields = [
            "Phylum",
            "Suborder",
            "Family",
            "Subfamily"
        ]

        # There's no way of doing update set from in sqlalchemy - so add it just as plain sql
        values = []
        for inherited_field in inherited_fields:
            values.append('"{inherited_field}" = COALESCE(s1."{inherited_field}", s2."{inherited_field}") '.format(inherited_field=inherited_field))

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

        print 'Updating dependent fields: SUCCESS'

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

    index_field_blacklist = ['multimedia']

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


if __name__ == '__main__':



    d = KeEMuSpecimensDatastore()
    # print d._dynamic_properties_view()
    # r = d.session.execute(d._dynamic_properties_view())
    # for x in r:
    #     print x

    c = d._dynamic_properties_view()
    # print c
    # print x
    # q =

    # c = CreateAsSelect('dyn1', d._dynamic_properties_view())
    # result = d.session.execute(c)
    # for x in result:
    #     print x


    # d.session.commit()

    #
    # print x
    #
    # result = session.execute(x)
    # # for row in result:
    # #     print row
    #

