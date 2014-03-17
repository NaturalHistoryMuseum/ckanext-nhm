#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""
from ke2sql.model.keemu import *

from ke2sql.model.keemu import specimen_sex_stage, catalogue_associated_record, catalogue_multimedia
from ke2sql.model.views import SpecimenTaxonomyView
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
from ckanext.nhm.lib.db import get_datastore_session, CreateTableAs
import csv
import sqlalchemy
import itertools
import abc
import ckan.model as model
import ckan.logic as logic
from itertools import chain

# TODO: replace / add to DwC
INSTITUTION_CODE = 'NHMUK'
IDENTIFIER_PREFIX = '%s:ecatalogue:' % INSTITUTION_CODE
IMAGE_URL = 'http://www.nhm.ac.uk/emu-classes/class.EMuMedia.php?irn=%s'

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

    resource_type = None
    session = None

    def __init__(self):
        self.session = get_datastore_session()

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

    def create_package(self, context):
        """
        Setup the CKAN datastore
        Return the datastore_resource_id
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
        # CHeck if table exists before dropping - need to manually check existence, as we will get an error if it's already a view
        if self.session.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{resource_id}')".format(resource_id=resource_id)).scalar():
            self.session.execute('DROP TABLE "{resource_id}"'.format(resource_id=resource_id))

        # Delete the view if it exists
        self.session.execute('DROP MATERIALIZED VIEW IF EXISTS "{resource_id}"'.format(resource_id=resource_id))

        # Create some types used across queries
        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'multimedia_t\')').scalar():
            self.session.execute('CREATE TYPE multimedia_t AS (url int, mime_type text, title text)')

        # Create the view
        self.session.execute('CREATE MATERIALIZED VIEW "{resource_id}" AS ({query})'.format(resource_id=resource_id, query=self.datastore_query()))

        # Create index on the view
        self.session.execute('CREATE UNIQUE INDEX "{resource_id}_idx" ON "{resource_id}" (_id)'.format(resource_id=resource_id))

        # TODO: Shall we add other indexes? Scientific name?

        self.session.commit()

        print 'Created datastore %s: SUCCESS' % self.name

    def update(self):
        """
        Update the datastore
        """
        # TODO: Update - at the moment this just drops and recreates. Need to refresh mat views
        self.create()



class KeEMuSpecimensDatastore(KeEMuDatastore):

    name = 'Specimens'
    description = 'Specimen records'

    package = {
        'name': u'nhm-collection25',
        'notes': u'The Natural History Museum\'s collection',
        'title': "Collection"
    }

    def datastore_query(self):

        # TODO: Create tables in the background, then create view. Minimal downtime
        # TODO: Move on complete determ stuff to here too.

        # Build a table containing all specimen data

        # create materialized view v_specimen_type as select irn, type from catalogue c where exists (select 1 from specimen where irn = c.irn);

        # CREATE UNIQUE INDEX irn_idx ON v_specimen_type (irn);
        # CREATE INDEX type_idx ON v_specimen_type (type);

        # models = [SpecimenModel, PartModel, DNAPrepModel, ParasiteCardModel, EggModel, FieldNotebookModel, NestModel, SilicaGelSpecimenModel, BotanySpecimenModel, PalaeontologySpecimenModel, MineralogySpecimenModel, MeteoritesSpecimenModel]

        from sqlalchemy.orm import class_mapper

        # for model in models:
        #     for col in model.__table__.columns:
        #
        #         if col.key in ['irn']:
        #             continue
        #
        #         print '%s,' % col

        # columns = list(itertools.chain.from_iterable(model.__table__.columns for model in models))
        #
        # for c in columns:
        #     print c.name
        #
        # raise SystemExit

        # TODO: alter user bubba set work_mem='500MB';


        schema = 'keemu'

        # Build a table with the current determination to use for each specimen
        # For part specimens, uses the parent record

        print 'Creating tmp_specimen_taxonomy table'

        self.session.execute(text('DROP TABLE IF EXISTS {schema}.tmp_specimen_taxonomy'.format(schema=schema)))

        # TODO: This should only select the first determination. Limit isn't working
        self.session.execute(text(
            """
            CREATE TABLE {schema}.tmp_specimen_taxonomy AS
                    (SELECT DISTINCT ON(d.specimen_irn) specimen_irn, taxonomy_irn
                    FROM {schema}.determination d
                    INNER JOIN keemu.specimen s ON s.irn = d.specimen_irn
                    ORDER BY d.specimen_irn, filed_as DESC LIMIT 1)
                UNION
                    (SELECT DISTINCT ON(s.irn) s.irn as specimen_irn, taxonomy_irn
                    FROM {schema}.SPECIMEN s
                    INNER JOIN keemu.part p ON p.irn = s.irn
                    INNER JOIN keemu.determination d ON p.parent_irn = d.specimen_irn
                    WHERE NOT EXISTS (SELECT 1 FROM keemu.determination WHERE specimen_irn = s.irn)
                    ORDER BY s.irn, filed_as DESC LIMIT 1)
            """.format(schema=schema)
        ))

        # Add primary key
        self.session.execute(text('ALTER TABLE {schema}.tmp_specimen_taxonomy ADD PRIMARY KEY (specimen_irn)'.format(schema=schema)))

        print 'Creating tmp_specimen table'

        self.session.execute('DROP TABLE IF EXISTS {schema}.tmp_specimen'.format(schema=schema))

        # Create a table containing all specimen data
        self.session.execute(
            """
            CREATE TABLE {schema}.tmp_specimen AS
                (SELECT
                    specimen.irn as _id,
                    specimen.collection_department,
                    specimen.collection_sub_department,
                    specimen.specimen_unit,
                    specimen.curation_unit,
                    specimen.catalogue_number,
                    specimen.preservation,
                    specimen.verbatim_label_data,
                    specimen.donor_name,
                    specimen.date_catalogued,
                    specimen.kind_of_collection,
                    specimen.specimen_count,
                    specimen.preparation,
                    specimen.preparation_type,
                    specimen.weight,
                    specimen.registration_code,
                    specimen.type_status,
                    specimen.date_identified_day,
                    specimen.date_identified_month,
                    specimen.date_identified_year,
                    specimen.identification_qualifier,
                    specimen.identified_by,
                    specimen.site_irn,
                    specimen.collection_event_irn,

                    part.parent_irn,
                    part.part_type,

                    dna_preparation.extraction_method,
                    dna_preparation.resuspended_in,
                    dna_preparation.total_volume,

                    parasite_card.barcode,

                    egg.clutch_size,
                    egg.set_mark,

                    nest.nest_shape,
                    nest.nest_site,

                    silica_gel.population_code,

                    botany.exsiccati,
                    botany.exsiccati_number,
                    botany.site_description,
                    botany.plant_description,
                    botany.habitat_verbatim,
                    botany.cultivated,
                    botany.plant_form,

                    palaeontology.catalogue_description,
                    palaeontology.stratigraphy_irn,

                    mineralogy.date_registered,
                    mineralogy.identification_as_registered,
                    mineralogy.occurrence,
                    mineralogy.commodity,
                    mineralogy.deposit_type,
                    mineralogy.texture,
                    mineralogy.identification_variety,
                    mineralogy.identification_other,
                    mineralogy.host_rock,

                    meteorite.meteorite_type,
                    meteorite.meteorite_group,
                    meteorite.chondrite_achondrite,
                    meteorite.meteorite_class,
                    meteorite.pet_type,
                    meteorite.pet_sub_type,
                    meteorite.recovery,
                    meteorite.recovery_date,
                    meteorite.recovery_weight
                FROM {schema}.specimen
                    LEFT OUTER JOIN {schema}.part ON part.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.dna_preparation ON dna_preparation.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.parasite_card ON parasite_card.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.egg ON egg.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.nest ON nest.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.silica_gel ON silica_gel.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.botany ON botany.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.palaeontology ON palaeontology.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.mineralogy ON mineralogy.irn = specimen.irn
                    LEFT OUTER JOIN {schema}.meteorite ON meteorite.irn = specimen.irn
                )
            """.format(schema=schema))

        print 'Indexing tmp_specimen table'

        # Create index on tmp_specimen
        self.session.execute('ALTER TABLE {schema}.tmp_specimen ADD PRIMARY KEY (_id)'.format(schema='keemu'))

        # Create types
        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'other_numbers_t\')').scalar():

            self.session.execute(
                """
                CREATE TYPE other_numbers_t
                AS (kind text, value text)
                """
            )

        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'sex_stage_t\')').scalar():

            self.session.execute(
                """
                CREATE TYPE sex_stage_t
                AS (count int, sex text, stage text)
                """
            )

        if not self.session.execute('SELECT EXISTS (select 1 from pg_type where typname = \'host_parasite_t\')').scalar():

            self.session.execute(
                """
                CREATE TYPE host_parasite_t
                AS (parasite_host text, stage text, irn int)
                """
            )

        # Create the query for the materialised view
        # I'm not using the full determination - just the current to keep this a little bit simpler
        # There are still a lot of fields, but many will be hidden in the front end - and only visible fields will downloaded
        query = """
                SELECT tmp.*,
                    t.*,
                    si.continent,
                    si.country,
                    si.state_province,
                    si.county,
                    si.locality,
                    si.vice_county,
                    si.parish,
                    si.town,
                    si.nearest_named_place,
                    si.ocean,
                    si.island_group,
                    si.island,
                    si.lake,
                    si.river_basin,
                    si.geodetic_datum,
                    si.georef_method,
                    si.latitude,
                    si.decimal_latitude,
                    si.longitude,
                    si.decimal_longitude,
                    si.minimum_elevation_in_meters,
                    si.maximum_elevation_in_meters,
                    si.minimum_depth_in_meters,
                    si.maximum_depth_in_meters,
                    si.mineral_complex,
                    si.mine,
                    si.mining_district,
                    si.tectonic_province,
                    si.geology_region,
                    ce.date_collected_from,
                    ce.time_collected_from,
                    ce.date_collected_to,
                    ce.time_collected_to,
                    ce.collection_event_code,
                    ce.collection_method,
                    ce.depth_from_metres,
                    ce.depth_to_metres,
                    ce.expedition_start_date,
                    ce.expedition_name,
                    ce.vessel_name,
                    ce.vessel_type,
                    ce.collector_name,
                    ce.collector_number,
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(mm.irn, mm.mime_type, mm.title)::multimedia_t
                            )
                        )
                    ) as "multimedia",
                    ARRAY_AGG(car.associated_irn) AS associated,
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(o.kind, o.value)::other_numbers_t
                            )
                        )
                    ) as "other_numbers",
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(ss.count, ss.sex, ss.stage)::sex_stage_t
                            )
                        )
                    ) as "sex_stage",
                    ARRAY_TO_JSON(
                        ARRAY_AGG(
                            ROW_TO_JSON(
                                ROW(hp.parasite_host, hp.stage, hp_t.irn)::host_parasite_t
                            )
                        )
                    ) as "host_parasite"
                FROM {schema}.tmp_specimen tmp
                LEFT OUTER JOIN {schema}.site si ON si.irn = tmp.site_irn
                LEFT OUTER JOIN {schema}.collection_event ce ON ce.irn = tmp.collection_event_irn
                LEFT OUTER JOIN {schema}.catalogue_multimedia cmm ON cmm.catalogue_irn = tmp._id
                  LEFT OUTER JOIN {schema}.multimedia mm ON mm.irn = cmm.multimedia_irn
                LEFT OUTER JOIN {schema}.catalogue_associated_record car ON car.catalogue_irn = tmp._id
                LEFT OUTER JOIN {schema}.other_numbers o ON o.irn = tmp._id
                LEFT OUTER JOIN {schema}.specimen_sex_stage sss ON sss.specimen_irn = tmp._id
                  LEFT OUTER JOIN {schema}.sex_stage ss ON ss.id = sss.sex_stage_id
                LEFT OUTER JOIN {schema}.tmp_specimen_taxonomy tmp_t ON tmp_t.specimen_irn = tmp._id
                  LEFT OUTER JOIN {schema}.taxonomy t ON t.irn = tmp_t.taxonomy_irn
                LEFT OUTER JOIN {schema}.host_parasite hp ON hp.parasite_card_irn = tmp._id
                  LEFT OUTER JOIN {schema}.taxonomy hp_t ON hp_t.irn = hp.taxonomy_irn
                LEFT OUTER JOIN {schema}.stratigraphy s ON s.irn = tmp.stratigraphy_irn
                  LEFT OUTER JOIN {schema}.stratigraphy_stratigraphic_unit ssu ON ssu.stratigraphy_irn = s.irn
                    LEFT OUTER JOIN {schema}.stratigraphic_unit su ON su.id = ssu.unit_id
                GROUP BY tmp._id, si.irn, ce.irn, t.irn
                """.format(schema=schema)

        return query

    def dwc_query(self):
        """
        Query for converting data from KE EMu into DwC record
        Only datasets with this method will show a DwC view
        """
        pass



                # si.continent,
                # si.country,
                # si.state_province,
                # si.county,
                # si.locality,
                # si.vice_county,
                # si.parish,
                # si.town,
                # si.nearest_named_place,
                # si.ocean,
                # si.island_group,
                # si.island,
                # si.lake,
                # si.river_basin,
                # si.geodetic_datum,
                # si.georef_method,
                # si.latitude,
                # si.decimal_latitude,
                # si.longitude,
                # si.decimal_longitude,
                # si.minimum_elevation_in_meters,
                # si.maximum_elevation_in_meters,
                # si.minimum_depth_in_meters,
                # si.maximum_depth_in_meters,
                # si.mineral_complex,
                # si.mine,
                # si.mining_district,
                # si.tectonic_province,
                # si.geology_region,
                # ce.date_collected_from,
                # ce.time_collected_from,
                # ce.date_collected_to,
                # ce.time_collected_to,
                # ce.collection_event_code,
                # ce.collection_method,
                # ce.depth_from_metres,
                # ce.depth_to_metres,
                # ce.expedition_start_date,
                # ce.expedition_name,
                # ce.vessel_name,
                # ce.vessel_type,
                # ce.collector_name,
                # ce.collector_number


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













# class KeEMuSpecimensDatastore(object):
#     """
#     KE EMu specimens datastore
#     """
#     name = 'Specimens'
#     description = 'Specimen records'
#     resource_type = 'nhm-specimens'
#     package = {
#         'name': u'nhm-collection24',
#         'notes': u'The Natural History Museum\'s collection',
#         'title': "Collection"
#     }
#
#     def datastore_query(self):
#         """
#         Query for building the KE EMu collections datastore
#         """
#         specimen = SpecimenModel.__table__
#         site = SiteModel.__table__
#         collection_event = CollectionEventModel.__table__
#         botany = BotanySpecimenModel.__table__
#
#         # Create a list of columns we want to retrieve
#         columns = []
#
#         def _field_filter(field):
#             if 'irn' in field.name:
#                 return False
#
#             if field.name.startswith('_'):
#                 return False
#
#             return True
#
#         # Loop through all the fields, applying _field_filter to remove the fields we don't want
#         for table in [specimen, site, collection_event]:
#             columns.append(itertools.ifilter(_field_filter, getattr(table, 'c')))
#
#         columns = list(itertools.chain.from_iterable(columns))
#
#         # Add the IRN as the _id field
#         columns.append(specimen.c.irn.label('_id'))
#
#         # TODO: Add more columns here
#
#         # Chain all the columns together into one list
#         query = select(columns)
#
#         query = query.select_from(specimen
#                                   .outerjoin(site, site.c.irn == specimen.c.site_irn)
#                                   .outerjoin(collection_event, collection_event.c.irn == specimen.c.collection_event_irn)
#                                   .outerjoin(botany, botany.c.irn == specimen.c.irn)
#                                   )
#
#         # TODO: TEMP - Remove this
#         query = query.limit(1)
#         return query
#
#     def dwc_query(self):
#         """
#         Query for converting data from KE EMu into DwC record
#         """
#         session = get_datastore_session()
#
#         query = session.query(
#             # Extra DwC fields
#             DwC.institution_code,
#             DwC.global_unique_identifier.label('GlobalUniqueIdentifier'),
#             DwC.related_catalogue_item.label('RelatedCatalogedItems'),
#             # Catalogue fields
#             SpecimenModel.ke_date_modified.label('modified'),
#             # Specimen fields
#             SpecimenModel.catalogue_number.label('CatalogNumber'),
#             SpecimenModel.type_status.label('TypeStatus'),
#             SpecimenModel.date_identified_day.label('DayIdentified'),
#             SpecimenModel.date_identified_month.label('MonthIdentified'),
#             SpecimenModel.date_identified_year.label('YearIdentified'),
#             DwC.other_numbers.label('OtherCatalogNumbers'),
#             DwC.collection_code.label('CollectionCode'),
#             # TODO: Put back after rerunning import
#             # SpecimenModel.specimen_count.label('IndividualCount'),
#             # SpecimenModel.preparation.label('Preparations'),
#             # SpecimenModel.preparation_type.label('PreparationType'),
#             # SpecimenModel.weight.label('ObservedWeight'),
#             # SpecimenModel.identification_qualifier.label('IdentificationQualifier'),
#             # SpecimenModel.identified_by.label('IdentifiedBy'),
#             # Sites data
#             SiteModel.continent.label('Continent'),
#             SiteModel.country.label('Country'),
#             SiteModel.state_province.label('StateProvince'),
#             SiteModel.county.label('County'),
#             SiteModel.locality.label('Locality'),
#             SiteModel.ocean.label('ContinentOcean'),
#             SiteModel.island_group.label('IslandGroup'),
#             SiteModel.island.label('Island'),
#             DwC.water_body.label('WaterBody'),
#             SiteModel.geodetic_datum.label('GeodeticDatum'),
#             SiteModel.georef_method.label('GeorefMethod'),
#             SiteModel.decimal_latitude.label('DecimalLatitude'),
#             SiteModel.decimal_longitude.label('DecimalLongitude'),
#             SiteModel.minimum_elevation_in_meters.label('MinimumElevationInMeters'),
#             SiteModel.maximum_elevation_in_meters.label('MaximumElevationInMeters'),
#             DwC.higher_geography.label('HigherGeography'),
#             # Collections event
#             DwC.date_collected_from_year.label('StartYearCollected'),
#             DwC.date_collected_from_month.label('StartMonthCollected'),
#             DwC.date_collected_from_day.label('StartDayCollected'),
#             DwC.date_collected_to_year.label('EndYearCollected'),
#             DwC.date_collected_to_month.label('EndMonthCollected'),
#             DwC.date_collected_to_day.label('EndDayCollected'),
#             DwC.date_collected_year.label('YearCollected'),
#             DwC.time_of_day.label('TimeOfDay'),
#             CollectionEventModel.time_collected_from.label('StartTimeOfDay'),
#             CollectionEventModel.time_collected_to.label('EndTimeOfDay'),
#             CollectionEventModel.collection_event_code.label('FieldNumber'),
#             CollectionEventModel.collection_method.label('samplingProtocol'),
#             DwC.min_depth.label('minimumDepthInMeters'),
#             DwC.max_depth.label('maximumDepthInMeters'),
#             # DwC.collector.label('Collector'),
#             CollectionEventModel.time_collected_to.label('CollectorNumber'),
#             # Taxonomy data
#             TaxonomyModel.scientific_name.label('ScientificName'),
#             TaxonomyModel.kingdom.label('Kingdom'),
#             TaxonomyModel.phylum.label('Phylum'),
#             TaxonomyModel.taxonomic_class.label('Class'),
#             TaxonomyModel.order.label('Order'),
#             TaxonomyModel.family.label('Family'),
#             TaxonomyModel.genus.label('Genus'),
#             TaxonomyModel.subgenus.label('Subgenus'),
#             TaxonomyModel.species.label('Species'),
#             TaxonomyModel.subspecies.label('Subspecies'),
#             TaxonomyModel.rank.label('taxonRank'),
#             TaxonomyModel.scientific_name_author.label('ScientificNameAuthor'),
#             TaxonomyModel.scientific_name_author_year.label('ScientificNameAuthorYear'),
#             DwC.higher_taxon.label('HigherTaxon'),
#             # Multimedia
#             DwC.images.label('associatedMedia'),
#             # Sex stage
#             DwC.sex.label('Sex'),
#             DwC.stage.label('LifeStage'),
#             # Botany
#             BotanySpecimenModel.__table__.c.habitat_verbatim.label('Habitat')
#
#         ).outerjoin(SpecimenModel.site)\
#             .outerjoin(SpecimenModel.collection_event)\
#             .outerjoin(SpecimenModel.site)\
#             .outerjoin(BotanySpecimenModel.__table__)\
#             .outerjoin(SpecimenTaxonomyView, SpecimenTaxonomyView.c.specimen_irn == SpecimenModel.irn)\
#             .outerjoin(TaxonomyModel, TaxonomyModel.irn == SpecimenTaxonomyView.c.taxonomy_irn)\
#
#         return query
#
#     def dwc_get_record(self, irn):
#         """
#         Get a record as DwC
#         """
#         query = self.dwc_query()
#         query = query.filter(CatalogueModel.irn == irn)
#         # Return record as a dict
#         return query.one().__dict__
#
#     def dwc_export(self, outfile):
#         """
#         Export as darwin core
#         """
#
#         query = self.dwc_query()
#         # TODO: Optimise this query. AT the moment I have to limit it to prevent memory timeouts
#         query = query.limit(10)
#         # TODO: yield_per?
#
#         # TODO: This is not working - and do we want to use PG COPY anyway?
#         f = csv.writer(open(outfile, 'wb'))
#         for record in query.all():
#             f.writerow(record)
#
#
#
#
# class KeEMuArtefactDatastore(object):
#     """
#     KE EMu artefacts datastore
#     """
#     name = 'Artefacts'
#     description = 'Artefacts'
#     package = {
#         'name': u'nhm-artefacts',
#         'notes': u'Artefacts from The Natural History Museum',
#         'title': "Artefacts"
#     }
#
#     def datastore_query(self):
#
#         tbl_datastore = Datastore.__table__
#         tbl_artefact = ArtefactModel.__table__
#
#         query = select([
#             tbl_datastore.c.irn.label('_id'),
#             Datastore.multimedia.label('Images'),
#             tbl_artefact.c.kind,
#             tbl_artefact.c.name,
#         ])
#
#         query = query.select_from(tbl_datastore.join(tbl_artefact, tbl_artefact.c.irn == tbl_datastore.c.irn))
#         return query
#
#
# # Query models
#
# class Datastore(Base):
#
#     __table__ = CatalogueModel.__table__
#
#      # Store the images and URL directly in the datastore, so we don't have to hack around with the API
#     multimedia = column_property(
#         select([
#             func.array_to_string(
#                 func.array_agg(
#                     # TODO: Add case to handle videos
#                     func.format(IMAGE_URL, catalogue_multimedia.c.multimedia_irn)), '; ')
#             ]
#         ).where(catalogue_multimedia.c.catalogue_irn == CatalogueModel.irn)
#     )
#
# class DwC(Base):
#
#     # TODO: I would much prefer this to convert from the datastore
#     # And then KE EMu database can be private (and include stuff like multimedia we wouldn't want to use)
#
#     __table__ = CatalogueModel.__table__
#     # Add calculated fields etc.,
#     institution_code = column_property(literal_column("'%s'" % INSTITUTION_CODE).label('institution_code'))
#     global_unique_identifier = column_property(IDENTIFIER_PREFIX + cast(CatalogueModel.__table__.c.irn, String))
#
#     # Subquery property to get related catalogue items
#     # http://stackoverflow.com/questions/7788288/sqlalchemy-subquery-for-suming-values-from-another-table
#     related_catalogue_item = column_property(
#         select([
#             func.array_to_string(
#                 func.array_agg(
#                     func.format(IDENTIFIER_PREFIX + '%s', catalogue_associated_record.c.associated_irn)), '; ')
#             ]
#         ).where(catalogue_associated_record.c.catalogue_irn==CatalogueModel.irn)
#     )
#
#     # Other numbers subquery
#     other_numbers = column_property(
#         select([
#             func.array_to_string(
#                 func.array_agg(OtherNumbersModel.value), '; ')
#             ]
#         ).where(OtherNumbersModel.irn==CatalogueModel.irn)
#     )
#
#     # Collection code (based on department: Zoology: ZOO, Paleo: PAL, Botany: BOT, Entom: BMNH(E))
#     # Warning: In KE EMu mineralogy has no collection code
#     collection_code = column_property(
#         case(
#             [(SpecimenModel.collection_department == 'Entomology', 'BMNH(E)')],
#             else_=func.upper(func.substr(SpecimenModel.collection_department, 0, 4))
#         )
#     )
#
#     # Water body uses lake > river basin > ocean
#     # TODO: Add Lake
#     water_body = column_property(
#         func.coalesce(
#             SiteModel.river_basin,
#             SiteModel.ocean
#         )
#     )
#
#     # Extract months years etc.,
#     date_collected_from_year = column_property(
#         func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})')
#     )
#
#     date_collected_from_month = column_property(
#         func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})')
#     )
#
#     date_collected_from_day = column_property(
#         func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
#     )
#
#     date_collected_to_year = column_property(
#         func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})')
#     )
#
#     date_collected_to_month = column_property(
#         func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})')
#     )
#
#     date_collected_to_day = column_property(
#         func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
#     )
#
#     # Use either collected from or if that's null, use to
#     date_collected_year = column_property(
#         func.coalesce(
#             func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})'),
#             func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})')
#         )
#     )
#
#     date_collected_month = column_property(
#         func.coalesce(
#             func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})'),
#             func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})')
#         )
#     )
#
#     date_collected_day = column_property(
#         func.coalesce(
#             func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})'),
#             func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
#         )
#     )
#
#     time_of_day = column_property(
#         func.coalesce(
#             CollectionEventModel.time_collected_from,
#             CollectionEventModel.time_collected_to
#         )
#     )
#
#     # Use expedition name if collector name is null
#     # TODO: Put back when rerun
#     # collector = column_property(
#     #     func.coalesce(
#     #         CollectionEventModel.collector_name,
#     #         CollectionEventModel.expedition_name
#     #     )
#     # )
#
#     # Use either Collection event depth or site depth
#     min_depth = column_property(
#         func.coalesce(
#             CollectionEventModel.depth_from_metres,
#             SiteModel.minimum_depth_in_meters
#         )
#     )
#
#         # Use either Collection event depth or site depth
#     max_depth = column_property(
#         func.coalesce(
#             CollectionEventModel.depth_to_metres,
#             SiteModel.maximum_depth_in_meters
#         )
#     )
#
#     sex = column_property(
#         select([
#             func.array_to_string(func.array_agg(SexStageModel.sex), '; ')
#             ],
#             from_obj=SexStageModel.__table__.join(specimen_sex_stage, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)
#         ).where(specimen_sex_stage.c.specimen_irn == CatalogueModel.irn).where(SexStageModel.sex != '')
#     )
#
#     # KE EMu is using SexAge field for DarAgeClass, which isn't right
#     # SexAge has values like 2 days etc., whereas it should be Juvenile etc.,
#     # DarAgeClass could also map to this field, but DarLifeStage is a better fit
#     stage = column_property(
#         select([
#             func.array_to_string(func.array_agg(SexStageModel.stage), '; ')
#             ],
#             from_obj=SexStageModel.__table__.join(specimen_sex_stage, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)
#         ).where(specimen_sex_stage.c.specimen_irn == CatalogueModel.irn).where(SexStageModel.stage != '')
#     )
#
#     # Images
#     images = column_property(
#         select([
#             func.array_to_string(
#                 func.array_agg(
#                     # TODO: Image URLS
#                     func.format('http://URL/%s', catalogue_multimedia.c.multimedia_irn)), '; ')
#             ]
#         ).where(catalogue_multimedia.c.catalogue_irn==CatalogueModel.irn)
#     )
#
#     # Make higher taxon list
#     higher_taxon = column_property(
#         func.concat_ws('; ', TaxonomyModel.kingdom,
#                        TaxonomyModel.phylum,
#                        TaxonomyModel.order,
#                        TaxonomyModel.suborder,
#                        TaxonomyModel.superfamily,
#                        TaxonomyModel.family,
#                        TaxonomyModel.subfamily,
#                        TaxonomyModel.genus,
#                        TaxonomyModel.subgenus
#         )
#     )
#
#     # Make higher taxon list
#     higher_geography = column_property(
#         func.concat_ws('; ', SiteModel.continent,
#                        SiteModel.country,
#                        SiteModel.state_province,
#                        SiteModel.county,
#                        SiteModel.nearest_named_place
#         )
#     )


if __name__ == '__main__':

    from sqlalchemy.orm import sessionmaker
    from ckanext.datastore.db import _get_engine
    data_dict = {'connection_url': 'postgresql://ckan_default:asdf@localhost/datastore_default'}
    engine = _get_engine(data_dict)
    session = sessionmaker(bind=engine)()

    d = KeEMuSpecimensDatastore()
    x = d.datastore_query()

    print x

    result = session.execute(x)
    # for row in result:
    #     print row

    session.commit()
