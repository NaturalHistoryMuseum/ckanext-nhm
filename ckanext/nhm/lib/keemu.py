#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""
import sys
from ke2sql.model.keemu import *

from ke2sql.model.keemu import specimen_sex_stage, catalogue_associated_record, catalogue_multimedia
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, column_property
from sqlalchemy.sql.expression import select, join
from sqlalchemy.sql import expression, functions
from sqlalchemy import text
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, Boolean, Date, UniqueConstraint, Enum, DateTime, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast
from sqlalchemy import literal_column
from sqlalchemy import case
from sqlalchemy import and_
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

# TODO: replace / add to DwC
INSTITUTION_CODE = 'NHMUK'
IDENTIFIER_PREFIX = '%s:ecatalogue:' % INSTITUTION_CODE
IMAGE_URL = 'http://www.nhm.ac.uk/emu-classes/class.EMuMedia.php?irn=%s'
MULTIMEDIA_URL = 'http://URL/%s'

VIEW = 'VIEW'
MATERIALIZED_VIEW = 'MATERIALIZED VIEW'
TABLE = 'TABLE'

Base = declarative_base()

# TODO: create_base_tables()
# The base table has all fields, so view is base.*: overkill?

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

    resource_type = None
    session = None

    def __init__(self):
        self.session = get_datastore_session()


        # data_dict = {'connection_url': 'postgresql://ckan_default:asdf@localhost/datastore_default'}
        #
        # self.engine = _get_engine(data_dict)
        # self.session = sessionmaker(bind=self.engine)

    @abc.abstractproperty
    def name(self):
        return None

    @abc.abstractproperty
    def description(self):
        return None

    @abc.abstractproperty
    def package(self):
        return None

    @abc.abstractmethod
    def datastore_query(self):
        """
        Return the select query to create the datastore
        """
        return None

    def get_views(self):
        return []

    def view_exists(self, view_name):
        return self.session.execute("SELECT EXISTS (select 1 from pg_class where relname = '{view_name}')".format(view_name=view_name)).scalar()

    def create_views(self):

        for view in self.get_views():

            # Does this object already exist?
            if self.view_exists(view['name']):

                if view['type'] is VIEW:
                    # If it's just a view and already exists, do nothing
                    print 'View %s already exists: SKIPPING' % view['name']
                    continue

                elif view['type'] is MATERIALIZED_VIEW:
                    # If the mat view already exists, refresh it
                    print 'Materialized view %s already exists: REFRESHING' % view['name']
                    self.session.execute(text('REFRESH MATERIALIZED VIEW {view_name}'.format(view_name=view['name'])))
                    continue

                else:
                    # Drop the table
                    self.session.execute('DROP TABLE IF EXISTS {view_name}'.format(view_name=view['name']))

            print 'Creating view %s' % view['name']

            c = CreateAsSelect(view['name'], view['func'](), view['type'])
            self.session.execute(c)

            print 'Adding index to view %s' % view['name']

            # And add a primary key for materialized and view
            if view['type'] is MATERIALIZED_VIEW:
                self.session.execute(text('CREATE UNIQUE INDEX {view_name}_irn_idx ON {view_name} (irn)'.format(view_name=view['name'])))
            elif view['type'] is TABLE:
                self.session.execute(text('ALTER TABLE {view_name} ADD PRIMARY KEY (irn)'.format(view_name=view['name'])))

            print 'Creating view %s: SUCCESS' % view['name']

            self.session.commit()

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

    def create(self):
        """
        Create the datastore
        """
        # Set up API context
        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}
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
                    'resource_type': self.resource_type
                }
            }

            datastore = logic.get_action('datastore_create')(context, datastore_params)
            resource_id = datastore['resource_id']

        print 'Creating datastore %s' % resource_id

        # Drop the table created by CKAN - we're going to replace it with a Materialised view
        # Check if table exists before dropping
        # Need to manually check existence, as we will get an error if it's already a view
        if self.session.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{resource_id}')".format(resource_id=resource_id)).scalar():
            self.session.execute('DROP TABLE "{resource_id}"'.format(resource_id=resource_id))

        # Create some types used across all queries
        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'multimedia_t\')').scalar():
            self.session.execute('CREATE TYPE multimedia_t AS (url int, mime_type text, title text)')

        # Create any views need to build the query
        self.create_views()

        # The source table which will be behind the materialised view
        source_table = '_source_%s' % resource_id

        self.session.execute('DROP TABLE IF EXISTS "{source_table}"'.format(source_table=source_table))

        c = CreateAsSelect(source_table, self.datastore_query())
        self.session.execute(c)

        print 'SUCCESS'

        # TODO: Full text
        # TODO: DwC Dates
        # TODO: Check all data and fields
        # TODO: Add more to dynamic properties

        # At this point, all of the source tables are in place
        # So create or refresh the materialised view
        if self.view_exists(resource_id):

            # Just refresh the materialised view
            # This was there will be no downtime for the front end user
            # Table will be unresponsive for the ~1 second it takes to refresh
            self.session.execute(text('REFRESH MATERIALIZED VIEW "{resource_id}"'.format(resource_id=resource_id)))

        else:

            # Create the view
            self.session.execute('CREATE MATERIALIZED VIEW "{resource_id}" AS (SELECT * FROM "{source_table}")'.format(resource_id=resource_id, source_table=source_table))
            # Create index on the view
            self.session.execute('CREATE UNIQUE INDEX "{resource_id}_idx" ON "{resource_id}" (_id)'.format(resource_id=resource_id))

            # TODO: Add other indexes? Scientific name?

        self.session.commit()

        print 'Created datastore %s: SUCCESS' % self.name


class KeEMuSpecimensDatastore(KeEMuDatastore):

    name = 'Specimens'
    description = 'Specimen records'

    package = {
        'name': u'nhm-collection25',
        'notes': u'The Natural History Museum\'s collection',
        'title': "Collection"
    }

    views = {}

    def get_views(self):

        return [
            {
                'name': '_geological_context_v',
                'func': self._geological_context_view,
                'type': TABLE  # Use a table where we want to add individual fields - primary key can be used in group clause
            },
            {
                'name': '_associated_records_v',
                'func': self._associated_records_view,
                'type': VIEW
            },
            {
                'name': '_taxonomy_v',
                'func': self._taxonomy_view,
                'type': TABLE
            },
            {
                'name': '_dynamic_properties_v',
                'func': self._dynamic_properties_view,
                'type': TABLE
            },
        ]

    def datastore_query(self, force_rebuild=False):

        q = self._dwc_query()

        # TODO: It's dynamic properties breaking this.
        # TODO: It doesn't need to be json. Just key=value.
        # TODO: And how fast if stripped down to non null only. That will be tiny!!

        # Add the dynamic properties field and joins
        # Needs to go here to prevent self referential queries in _dwc_query
        # metadata = MetaData(self.session.bind)
        # _dynamic_properties_v = Table('_dynamic_properties_v', metadata, autoload=True)
        # q = q.select_from(q.froms[0].join(_dynamic_properties_v, CatalogueModel.__table__.c.irn == _dynamic_properties_v.c.irn))
        # q = q.column(_dynamic_properties_v.c.properties)
        # q = q.group_by(_dynamic_properties_v.c.irn)

        return q

    def _dynamic_properties_view(self):

        qs = []

        for model in itertools.chain([SpecimenModel], SpecimenModel.__subclasses__(), PartModel.__subclasses__()):

        # for model in itertools.chain([SpecimenModel]):

            if model is StubModel:
                continue

            # Get all columns not mapped to dwc
            columns = self.dwc_get_unmapped(model)

            # Get a list of all tables
            # Specimen, Site and Collection events will be handled separately
            tables = set([column.table for column in columns if column.table not in [SpecimenModel.__table__, SiteModel.__table__, CollectionEventModel.__table__]])

            # Create a type name based on the tables used (site and collection event are universal so are excluded)
            # CREATE TYPE name_t AS (f1 int, f2 text, f3 text)
            type_name = '_'.join(t.name for t in tables) + '_ty'
            type_cols = ', '.join('%s %s' % (c.name, c.type) for c in columns)

            # Drop type if it exists - this code is only called on rebuilding, so no overhead
            self.session.execute('DROP TYPE IF EXISTS {type_name}'.format(type_name=type_name))
            self.session.execute('CREATE TYPE {type_name} AS ({type_cols})'.format(type_name=type_name, type_cols=type_cols))

            q = select([
                SpecimenModel.__table__.c.irn,
                func.array_to_json(
                    func.array_agg(
                        # Doesn't seem to be an easy way to specify row::type, so am just using a literal
                        literal_column('row(%s)::%s' % (', '.join('%s' % c for c in columns), type_name))
                    )
                ).label('properties')
            ])

            # Build select from (for the joins)
            select_from = SpecimenModel.__table__
            for table in tables:
                select_from = select_from.join(table, table.c.irn == SpecimenModel.__table__.c.irn)

            # Add joins to events and sites
            select_from = select_from.outerjoin(SiteModel, SiteModel.__table__.c.irn == SpecimenModel.__table__.c.site_irn)
            select_from = select_from.outerjoin(CollectionEventModel, CollectionEventModel.__table__.c.irn == SpecimenModel.__table__.c.collection_event_irn)

            q = q.select_from(select_from)

            # Only select a particular type - this does mean more and a slower query - but ensures data is correct
            q = q.where(CatalogueModel.__table__.c.type == model.__mapper_args__['polymorphic_identity'])

            q = q.group_by(SpecimenModel.__table__.c.irn)

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

    def _dwc_query(self):
        """
        Query for converting data from KE EMu into DwC record
        Only datasets with this method will show a DwC view
        """

        # Reflected views
        metadata = MetaData(self.session.bind)
        # Annoyingly, sqlalchemy doesn't support reflection of materialised views
        # See https://bitbucket.org/zzzeek/sqlalchemy/issue/2891/support-materialized-views-in-postgresql
        # For now, need to use either TABLE or VIEW if reflection is needed
        _geological_context_v = Table('_geological_context_v', metadata, autoload=True)
        _associated_records_v = Table('_associated_records_v', metadata, autoload=True)
        _taxonomy_v = Table('_taxonomy_v', metadata, autoload=True)

        q = select([

            # Catalogue model
            CatalogueModel.irn.label('_id'),
            CatalogueModel.ke_date_modified.label('modified'),
            literal_column("'%s'::text" % INSTITUTION_CODE).label('InstitutionCode'),
            func.format(IDENTIFIER_PREFIX + '%s', CatalogueModel.irn),

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
            # These need to be parsed into StartYearCollected
            CollectionEventModel.date_collected_from,
            CollectionEventModel.date_collected_to,
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
            _taxonomy_v.c.scientific_name.label('scientificName'),
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
            _taxonomy_v.c.scientific_name_author.label('ScientificName'),
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
        #
        # # Determination
        select_from = select_from.outerjoin(_taxonomy_v, _taxonomy_v.c.irn == SpecimenModel.__table__.c.irn)

        # Geological context
        select_from = select_from.outerjoin(_geological_context_v, _geological_context_v.c.irn == SpecimenModel.__table__.c.irn)

        q = q.select_from(select_from)

        # Add group by clauses so my aggregates work
        q = q.group_by(CatalogueModel.__table__.c.irn)
        q = q.group_by(SpecimenModel.__table__.c.irn)
        q = q.group_by(SiteModel.__table__.c.irn)
        q = q.group_by(CollectionEventModel.__table__.c.irn)
        q = q.group_by(BotanySpecimenModel.__table__.c.irn)
        q = q.group_by(_geological_context_v.c.irn)
        q = q.group_by(_taxonomy_v.c.irn)

        q = q.where(CatalogueModel.type != 'stub')

        return q


    def dwc_get_mapped_columns(self):
        """
        Return a list of all columns in the DwC query
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

    def dwc_get_unmapped(self, model):
        """
        For a model, get all unmapped DwC fields
        """

        field_mappings = self.dwc_get_mapped_columns()

        # Filter out DwC fields / IRN / Foreign Keys
        def _field_filter(field):

            if field in field_mappings:
                return False

            if 'irn' in field.key:
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

    def def_list_all_unmapped(self):
        """
        Output a list of all unmapped fields
        """
        unmapped_fields = OrderedDict()

        for model in itertools.chain([SpecimenModel], SpecimenModel.__subclasses__(), PartModel.__subclasses__()):

            for field in self.dwc_get_unmapped(model):

                try:

                    if model.__table__.name not in unmapped_fields[field.name]:
                        unmapped_fields[field.name].append(model.__table__.name)

                except KeyError:
                    unmapped_fields[field.name] = [model.__table__.name]

        for unmapped_field, models in unmapped_fields.items():
            print '%s\t%s' % (unmapped_field, ';'.join(models))


class KeEMuIndexlotDatastore(object):
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

        query = """
                SELECT i.irn as _id,
                    i.material,
                    i.is_type,
                    i.media,
                    i.kind_of_material,
                    i.kind_of_media,
                    t.scientific_name,
                    t.kingdom,
                    t.phylum,
                    t.taxonomic_class,
                    t.order,
                    t.suborder,
                    t.superfamily,
                    t.family,
                    t.subfamily,
                    t.genus,
                    t.subgenus,
                    t.species,
                    t.subspecies,
                    t.validity,
                    t.rank as taxonomic_rank,
                    t.scientific_name_author,
                    t.scientific_name_author_year,
                    t.currently_accepted_name,
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(count,sex,types,stage,primary_type_number)::material_t
                            )
                        )
                    ) as "material_detail",
                    to_tsvector(
                      concat_ws(',',
                        ARRAY_TO_STRING(ARRAY_AGG(ARRAY[(sex, types, stage, primary_type_number)]::text), ','),
                        i.kind_of_material,
                        i.kind_of_media,
                        t.scientific_name,
                        t.kingdom,
                        t.phylum,
                        t.taxonomic_class,
                        t.order,
                        t.suborder,
                        t.superfamily,
                        t.family,
                        t.subfamily,
                        t.genus,
                        t.subgenus,
                        t.species,
                        t.subspecies,
                        t.validity,
                        t.rank,
                        t.scientific_name_author,
                        t.scientific_name_author_year
                      )
                    ) as _full_text,
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(mm.irn, mm.mime_type, mm.title)::multimedia_t
                            )
                        )
                    ) as "multimedia"
                FROM {schema}.indexlot i
                LEFT OUTER JOIN {schema}.indexlot_material m ON m.irn = i.irn
                LEFT OUTER JOIN {schema}.taxonomy t ON t.irn = i.taxonomy_irn
                LEFT OUTER JOIN {schema}.catalogue_multimedia cmm ON cmm.catalogue_irn = i.irn
                  LEFT OUTER JOIN {schema}.multimedia mm ON mm.irn = cmm.multimedia_irn
                GROUP BY i.irn, t.irn
                """.format(schema='keemu')

        return query


class KeEMuArtefactDatastore(object):
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

    def datastore_query(self):

        query = """
                SELECT a.irn as _id,
                    a.kind,
                    a.name,
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(m.irn, m.mime_type, m.title)::multimedia_t
                            )
                        )
                    ) as "multimedia",
                    to_tsvector(
                      concat_ws(',',
                        a.kind,
                        a.name
                      )
                    ) as _full_text
                FROM {schema}.artefact a
                LEFT OUTER JOIN {schema}.catalogue_multimedia cm ON cm.catalogue_irn = a.irn
                INNER JOIN {schema}.multimedia m ON m.irn = cm.multimedia_irn
                GROUP BY a.irn
                """.format(schema='keemu')

        return query



if __name__ == '__main__':

    from sqlalchemy.orm import sessionmaker
    from ckanext.datastore.db import _get_engine
    data_dict = {'connection_url': 'postgresql://ckan_default:asdf@localhost/datastore_default'}
    engine = _get_engine(data_dict)
    session = sessionmaker(bind=engine)()

    d = KeEMuSpecimensDatastore()
    d.create()

    # x = d._taxonomy_view()
    # print x
    # q =

    # c = CreateAsSelect('dwc4', d.datastore_query())
    # session.execute(c)
    # session.commit()

    #
    # print x
    #
    # result = session.execute(x)
    # # for row in result:
    # #     print row
    #

