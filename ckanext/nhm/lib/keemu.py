#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import pylons
from ckanext.datastore.db import _get_engine
from sqlalchemy.orm import Query
from sqlalchemy.orm import sessionmaker
from ke2sql.model.keemu import CatalogueModel, SpecimenModel, OtherNumbersModel, SiteModel, CollectionEventModel, TaxonomyModel, SexStageModel, BotanySpecimenModel, ArtefactModel
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

INSTITUTION_CODE = 'NHMUK'
IDENTIFIER_PREFIX = '%s:ecatalogue:' % INSTITUTION_CODE
IMAGE_URL = 'http://www.nhm.ac.uk/emu-classes/class.EMuMedia.php?irn=%s'

Base = declarative_base()

class Datastore(Base):

    __table__ = CatalogueModel.__table__

     # Store the images and URL directly in the datastore, so we don't have to hack around with the API
    multimedia = column_property(
        select([
            func.array_to_string(
                func.array_agg(
                    # TODO: Add case to handle videos
                    func.format(IMAGE_URL, catalogue_multimedia.c.multimedia_irn)), '; ')
            ]
        ).where(catalogue_multimedia.c.catalogue_irn == CatalogueModel.irn)
    )



class DwC(Base):

    __table__ = CatalogueModel.__table__
    # Add calculated fields etc.,
    institution_code = column_property(literal_column("'%s'" % INSTITUTION_CODE).label('institution_code'))
    global_unique_identifier = column_property(IDENTIFIER_PREFIX + cast(CatalogueModel.__table__.c.irn, String))

    # Subquery property to get related catalogue items
    # http://stackoverflow.com/questions/7788288/sqlalchemy-subquery-for-suming-values-from-another-table
    related_catalogue_item = column_property(
        select([
            func.array_to_string(
                func.array_agg(
                    func.format(IDENTIFIER_PREFIX + '%s', catalogue_associated_record.c.associated_irn)), '; ')
            ]
        ).where(catalogue_associated_record.c.catalogue_irn==CatalogueModel.irn)
    )

    # Other numbers subquery
    other_numbers = column_property(
        select([
            func.array_to_string(
                func.array_agg(OtherNumbersModel.value), '; ')
            ]
        ).where(OtherNumbersModel.irn==CatalogueModel.irn)
    )

    # Collection code (based on department: Zoology: ZOO, Paleo: PAL, Botany: BOT, Entom: BMNH(E))
    # Warning: In KE EMu mineralogy has no collection code
    collection_code = column_property(
        case(
            [(SpecimenModel.collection_department == 'Entomology', 'BMNH(E)')],
            else_=func.upper(func.substr(SpecimenModel.collection_department, 0, 4))
        )
    )

    # Water body uses lake > river basin > ocean
    # TODO: Add Lake
    water_body = column_property(
        func.coalesce(
            SiteModel.river_basin,
            SiteModel.ocean
        )
    )

    # Extract months years etc.,
    date_collected_from_year = column_property(
        func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})')
    )

    date_collected_from_month = column_property(
        func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})')
    )

    date_collected_from_day = column_property(
        func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
    )

    date_collected_to_year = column_property(
        func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})')
    )

    date_collected_to_month = column_property(
        func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})')
    )

    date_collected_to_day = column_property(
        func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
    )

    # Use either collected from or if that's null, use to
    date_collected_year = column_property(
        func.coalesce(
            func.substring(CollectionEventModel.date_collected_from, '([0-9]{4})'),
            func.substring(CollectionEventModel.date_collected_to, '([0-9]{4})')
        )
    )

    date_collected_month = column_property(
        func.coalesce(
            func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-([0-9]{2})'),
            func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-([0-9]{2})')
        )
    )

    date_collected_day = column_property(
        func.coalesce(
            func.substring(CollectionEventModel.date_collected_from, '[0-9]{4}-[0-9]{2}-([0-9]{2})'),
            func.substring(CollectionEventModel.date_collected_to, '[0-9]{4}-[0-9]{2}-([0-9]{2})')
        )
    )

    time_of_day = column_property(
        func.coalesce(
            CollectionEventModel.time_collected_from,
            CollectionEventModel.time_collected_to
        )
    )

    # Use expedition name if collector name is null
    # TODO: Put back when rerun
    # collector = column_property(
    #     func.coalesce(
    #         CollectionEventModel.collector_name,
    #         CollectionEventModel.expedition_name
    #     )
    # )

    # Use either Collection event depth or site depth
    min_depth = column_property(
        func.coalesce(
            CollectionEventModel.depth_from_metres,
            SiteModel.minimum_depth_in_meters
        )
    )

        # Use either Collection event depth or site depth
    max_depth = column_property(
        func.coalesce(
            CollectionEventModel.depth_to_metres,
            SiteModel.maximum_depth_in_meters
        )
    )

    sex = column_property(
        select([
            func.array_to_string(func.array_agg(SexStageModel.sex), '; ')
            ],
            from_obj=SexStageModel.__table__.join(specimen_sex_stage, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)
        ).where(specimen_sex_stage.c.specimen_irn == CatalogueModel.irn).where(SexStageModel.sex != '')
    )

    # KE EMu is using SexAge field for DarAgeClass, which isn't right
    # SexAge has values like 2 days etc., whereas it should be Juvenile etc.,
    # DarAgeClass could also map to this field, but DarLifeStage is a better fit
    stage = column_property(
        select([
            func.array_to_string(func.array_agg(SexStageModel.stage), '; ')
            ],
            from_obj=SexStageModel.__table__.join(specimen_sex_stage, SexStageModel.__table__.c.id == specimen_sex_stage.c.sex_stage_id)
        ).where(specimen_sex_stage.c.specimen_irn == CatalogueModel.irn).where(SexStageModel.stage != '')
    )

    # Images
    images = column_property(
        select([
            func.array_to_string(
                func.array_agg(
                    # TODO: Image URLS
                    func.format('http://URL/%s', catalogue_multimedia.c.multimedia_irn)), '; ')
            ]
        ).where(catalogue_multimedia.c.catalogue_irn==CatalogueModel.irn)
    )

    # Make higher taxon list
    higher_taxon = column_property(
        func.concat_ws('; ', TaxonomyModel.kingdom,
                       TaxonomyModel.phylum,
                       TaxonomyModel.order,
                       TaxonomyModel.suborder,
                       TaxonomyModel.superfamily,
                       TaxonomyModel.family,
                       TaxonomyModel.subfamily,
                       TaxonomyModel.genus,
                       TaxonomyModel.subgenus
        )
    )

    # Make higher taxon list
    higher_geography = column_property(
        func.concat_ws('; ', SiteModel.continent,
                       SiteModel.country,
                       SiteModel.state_province,
                       SiteModel.county,
                       SiteModel.nearest_named_place
        )
    )


def keemu_init_datastore(datastore_resource_id, query):
    """
    Create a table in the datastore using datastore query
    If table exists, it will be destroyed
    CREATE TABLE [datastore_table] as [SQL]
    """
    session = get_datastore_session()
    # Drop the table if it already exists
    session.execute(sqlalchemy.text(u'DROP TABLE IF EXISTS "%s"' % datastore_resource_id))
    session.execute(CreateTableAs(datastore_resource_id, query))
    # Hack to add _full_text field
    # CKAN would handle this, but the API is slow when adding 3.5 million records
    session.execute(u'ALTER TABLE "{table}" ADD COLUMN _full_text tsvector'.format(table=datastore_resource_id))
    # Get all text fields we want to index
    text_columns = session.execute(sqlalchemy.text(u'SELECT STRING_AGG(QUOTE_IDENT(column_name), \', \') FROM information_schema.columns WHERE table_name = \'{table}\' and data_type = \'character varying\''.format(table=datastore_resource_id))).scalar()
    # Populate _full_text with all text fields
    session.execute(sqlalchemy.text(u'UPDATE "{table}" set _full_text = to_tsvector(ARRAY_TO_STRING(ARRAY[{text_columns}], \' \'))'.format(table=datastore_resource_id, text_columns=text_columns)))
    session.commit()


def _keemu_collection_datastore_query():
    """
    Convert data from KE EMu into flat datastore record
    """

    # Use a select so we can use CreateTableAs which requires Select
    # We also don't want any of the ORM functionality

    specimen = SpecimenModel.__table__
    site = SiteModel.__table__
    collection_event = CollectionEventModel.__table__
    botany = BotanySpecimenModel.__table__

    # Create a list of columns we want to retrieve
    columns = []

    def _field_filter(field):
        if 'irn' in field.name:
            return False

        if field.name.startswith('_'):
            return False

        return True

    # Loop through all the fields, applying _field_filter to remove the fields we don't want
    for table in [specimen, site, collection_event]:
        columns.append(itertools.ifilter(_field_filter, getattr(table, 'c')))

    columns = list(itertools.chain.from_iterable(columns))

    # Add the IRN as the _id field
    columns.append(specimen.c.irn.label('_id'))

    # TODO: Add more columns here

    # Chain all the columns together into one list
    query = select(columns)

    query = query.select_from(specimen
                              .outerjoin(site, site.c.irn == specimen.c.site_irn)
                              .outerjoin(collection_event, collection_event.c.irn == specimen.c.collection_event_irn)
                              .outerjoin(botany, botany.c.irn == specimen.c.irn)
                              )

    # TODO: TEMP - Remove this
    # query = query.limit(1)
    return query

def _keemu_artefacts_datastore_query():

    tbl_datastore = Datastore.__table__
    tbl_artefact = ArtefactModel.__table__

    query = select([
        tbl_datastore.c.irn.label('_id'),
        Datastore.multimedia.label('Images'),
        tbl_artefact.c.kind,
        tbl_artefact.c.name,
    ])

    query = query.select_from(tbl_datastore.join(tbl_artefact, tbl_artefact.c.irn == tbl_datastore.c.irn))
    return query

def keemu_init_collection_datastore(datastore_resource_id):
    """
    Create table for the collection datastore
    """
    query = _keemu_collection_datastore_query()
    keemu_init_datastore(datastore_resource_id, query)

def keemu_init_artefacts_datastore(datastore_resource_id):
    """
    Create table for the artefacts datastore
    """
    query = _keemu_artefacts_datastore_query()
    keemu_init_datastore(datastore_resource_id, query)

def keemu_update_collection_datastore(datastore_table):
    """
    Update collection datastore
    """
    pass

def keemu_update_artefact_datastore(datastore_table):
    """
    Update artefact datastore
    """
    pass

def _keemu_darwin_core_query():
    """
    Query for converting data from KE EMu into DwC record
    """
    session = get_datastore_session()

    query = session.query(
        # Extra DwC fields
        DwC.institution_code,
        DwC.global_unique_identifier.label('GlobalUniqueIdentifier'),
        DwC.related_catalogue_item.label('RelatedCatalogedItems'),
        # Catalogue fields
        SpecimenModel.ke_date_modified.label('modified'),
        # Specimen fields
        SpecimenModel.catalogue_number.label('CatalogNumber'),
        SpecimenModel.type_status.label('TypeStatus'),
        SpecimenModel.date_identified_day.label('DayIdentified'),
        SpecimenModel.date_identified_month.label('MonthIdentified'),
        SpecimenModel.date_identified_year.label('YearIdentified'),
        DwC.other_numbers.label('OtherCatalogNumbers'),
        DwC.collection_code.label('CollectionCode'),
        # TODO: Put back after rerunning import
        # SpecimenModel.specimen_count.label('IndividualCount'),
        # SpecimenModel.preparation.label('Preparations'),
        # SpecimenModel.preparation_type.label('PreparationType'),
        # SpecimenModel.weight.label('ObservedWeight'),
        # SpecimenModel.identification_qualifier.label('IdentificationQualifier'),
        # SpecimenModel.identified_by.label('IdentifiedBy'),
        # Sites data
        SiteModel.continent.label('Continent'),
        SiteModel.country.label('Country'),
        SiteModel.state_province.label('StateProvince'),
        SiteModel.county.label('County'),
        SiteModel.locality.label('Locality'),
        SiteModel.ocean.label('ContinentOcean'),
        SiteModel.island_group.label('IslandGroup'),
        SiteModel.island.label('Island'),
        DwC.water_body.label('WaterBody'),
        SiteModel.geodetic_datum.label('GeodeticDatum'),
        SiteModel.georef_method.label('GeorefMethod'),
        SiteModel.decimal_latitude.label('DecimalLatitude'),
        SiteModel.decimal_longitude.label('DecimalLongitude'),
        SiteModel.minimum_elevation_in_meters.label('MinimumElevationInMeters'),
        SiteModel.maximum_elevation_in_meters.label('MaximumElevationInMeters'),
        DwC.higher_geography.label('HigherGeography'),
        # Collections event
        DwC.date_collected_from_year.label('StartYearCollected'),
        DwC.date_collected_from_month.label('StartMonthCollected'),
        DwC.date_collected_from_day.label('StartDayCollected'),
        DwC.date_collected_to_year.label('EndYearCollected'),
        DwC.date_collected_to_month.label('EndMonthCollected'),
        DwC.date_collected_to_day.label('EndDayCollected'),
        DwC.date_collected_year.label('YearCollected'),
        DwC.time_of_day.label('TimeOfDay'),
        CollectionEventModel.time_collected_from.label('StartTimeOfDay'),
        CollectionEventModel.time_collected_to.label('EndTimeOfDay'),
        CollectionEventModel.collection_event_code.label('FieldNumber'),
        CollectionEventModel.collection_method.label('samplingProtocol'),
        DwC.min_depth.label('minimumDepthInMeters'),
        DwC.max_depth.label('maximumDepthInMeters'),
        # DwC.collector.label('Collector'),
        CollectionEventModel.time_collected_to.label('CollectorNumber'),
        # Taxonomy data
        TaxonomyModel.scientific_name.label('ScientificName'),
        TaxonomyModel.kingdom.label('Kingdom'),
        TaxonomyModel.phylum.label('Phylum'),
        TaxonomyModel.taxonomic_class.label('Class'),
        TaxonomyModel.order.label('Order'),
        TaxonomyModel.family.label('Family'),
        TaxonomyModel.genus.label('Genus'),
        TaxonomyModel.subgenus.label('Subgenus'),
        TaxonomyModel.species.label('Species'),
        TaxonomyModel.subspecies.label('Subspecies'),
        TaxonomyModel.rank.label('taxonRank'),
        TaxonomyModel.scientific_name_author.label('ScientificNameAuthor'),
        TaxonomyModel.scientific_name_author_year.label('ScientificNameAuthorYear'),
        DwC.higher_taxon.label('HigherTaxon'),
        # Multimedia
        DwC.images.label('associatedMedia'),
        # Sex stage
        DwC.sex.label('Sex'),
        DwC.stage.label('LifeStage'),
        # Botany
        BotanySpecimenModel.__table__.c.habitat_verbatim.label('Habitat')

    ).outerjoin(SpecimenModel.site)\
        .outerjoin(SpecimenModel.collection_event)\
        .outerjoin(SpecimenModel.site)\
        .outerjoin(BotanySpecimenModel.__table__)\
        .outerjoin(SpecimenTaxonomyView, SpecimenTaxonomyView.c.specimen_irn == SpecimenModel.irn)\
        .outerjoin(TaxonomyModel, TaxonomyModel.irn == SpecimenTaxonomyView.c.taxonomy_irn)\

    return query


def keemu_get_darwin_core(irn):
    """
    Get a record as DwC
    """

    query = _keemu_darwin_core_query()
    query = query.filter(CatalogueModel.irn == irn)
    # Return record as a dict
    return query.one().__dict__

def keemu_export_darwin_core(outfile):
    """
    Export as darwin core
    """

    query = _keemu_darwin_core_query()
    # TODO: Optimise this query. AT the moment I have to limit it to prevent memory timeouts
    query = query.limit(10)
    # TODO: yield_per?

    # TODO: This is not working - and do we want to use PG COPY anyway?
    f = csv.writer(open(outfile, 'wb'))
    for record in query.all():
        f.writerow(record)


if __name__ == '__main__':
    r = keemu_get_darwin_core(1)
    print r
