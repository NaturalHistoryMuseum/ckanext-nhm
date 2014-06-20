from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
from ckanext.nhm.controllers.record import RecordController
from collections import OrderedDict

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class SpecimenController(RecordController):
    """
    Controller for displaying a specimen record
    """

    # List of fields and groups
    field_groups = OrderedDict([
        ('Record', [
            ('occurrenceID', 'Identifier'),
            ('modified', 'Date modified'),
            ('created', 'Date created'),
            ('recordType', 'Record type'),
            ('registrationCode', 'Registration code'),
            ('kindOfObject', 'Kind of object'),
        ]),
        ('Classification', [
            ('scientificName', 'Scientific name'),
            ('scientificNameAuthorship', 'Authorship'),
            ('kingdom', 'Kingdom'),
            ('phylum', 'Phylum'),
            ('class', 'Class'),
            ('order', 'Order'),
            ('family', 'Family'),
            ('genus', 'Genus'),
            ('subgenus', 'Subgenus'),
            ('specificEpithet', 'Species'),
            ('infraspecificEpithet', 'Subspecies'),
            ('higherClassification', 'Higher classification'),
            ('taxonRank', 'Rank')
        ]),
        ('Location', [
            ('siteDescription', 'Site description'),
            ('locality', 'Locality'),
            ('stateProvince', 'State / province'),
            ('mine', 'Mine'),
            ('miningDistrict', 'Mining district'),
            ('country', 'Country'),
            ('continent', 'Continent'),
            ('island', 'Island'),
            ('islandGroup', 'Island group'),
            ('waterBody', 'Water body'),
            ('higherGeography', 'Higher geography'),

            ('decimalLatitude','Decimal latitude'),
            ('decimalLongitude','Decimal longitude'),
            ('geodeticDatum','Geodetic datum'),
            ('georeferenceProtocol','Georeferencing protocol'),

            ('minimumElevationInMeters','Minimum elevation (meters)'),
            ('maximumElevationInMeters','Maximum elevation (meters)'),
            ('minimumDepthInMeters','Minimum depth (meters)'),
            ('maximumDepthInMeters','Maximum depth (meters)'),
        ]),
        ('Collection event', [
            ('recordNumber', 'Collector number'),
            ('year', 'Collection date'),  # Year, month & day are joined into one. We use year so the fields match up
            ('month', ),  # Added to year, so no label
            ('day', ),
            ('recordedBy', 'Collector'),
            ('eventTime', 'Collection time'),
            ('habitat', 'Habitat'),
            ('fieldNumber', 'Field number'),
        ]),
        ('Identification', [
            ('identifiedBy', 'Identified by'),
            ('dateIdentified', 'Date identified'),
            ('identificationQualifier', 'Identification qualifier'),
            ('typeStatus', 'Type status'),
            ('identificationAsRegistered', 'Identification as registered'),
        ]),
        ('Specimen', [
            ('catalogNumber', 'Catalogue number'),
            ('collectionCode', 'Collection code'),
            ('subDepartment', 'Collection sub-department'),
            ('otherCatalogNumbers', 'Other catalogue numbers'),
            ('preparations', 'Preparations'),
            ('preparationType', 'Preparation type'),
            ('preservative', 'Preservative'),
            ('collectionKind', 'Collection kind'),
            ('collectionName', 'Collection name'),
            ('donorName', 'Donor name'),
            ('kindOfCollection', 'Kind of collection'),
            ('observedWeight', 'Weight'),
            ('individualCount', 'Count'),
            ('sex', 'Sex'),
            ('lifeStage', 'Stage'),
        ]),
        ('Mineralogy', [
            ('dateRegistered', 'Date registered'),
            ('occurrence', 'occurrence'),
            ('commodity', 'Commodity'),
            ('depositType', 'Deposit type'),
            ('texture', 'Texture'),
            ('identificationVariety', 'Identification variety'),
            ('identificationOther', 'Other identification'),
            ('hostRock', 'Host rock'),
            ('age', 'Age'),
            ('ageType', 'Age type'),
            ('geologyRegion', 'Geology region'),
            ('mineralComplex', 'Mineral complex'),
            ('earliestEonOrLowestEonothem', 'Earliest eon or lowest eonothem'),
            ('latestEonOrHighestEonothem', 'Latest eon or highest eonothem'),
            ('earliestEraOrLowestErathem', 'Earliest era or lowest erathem'),
            ('latestEraOrHighestErathem', 'Latest era or highest erathem'),
            ('earliestPeriodOrLowestSystem', 'Earliest period or lowest system'),
            ('latestPeriodOrHighestSystem', 'Latest period or highest system'),
            ('earliestEpochOrLowestSeries', 'Earliest epoch or lowest series'),
            ('latestEpochOrHighestSeries', 'Latest epoch or highest series'),
            ('earliestAgeOrLowestStage', 'Earliest age or lowest stage'),
            ('latestAgeOrHighestStage', 'Latest age or highest stage'),
            ('lowestBiostratigraphicZone', 'Lowest biostratigraphic zone'),
            ('highestBiostratigraphicZone', 'Highest biostratigraphic zone'),
            ('group', 'Group'),
            ('formation', 'Formation'),
            ('member', 'Member'),
            ('bed', 'Bed'),
            ('chronostratigraphy', 'Chronostratigraphy'),
            ('lithostratigraphy', 'Lithostratigraphy'),
            ('tectonicProvince', 'Tectonic province'),
            ('registeredWeight', 'Registered weight'),
            ('registeredWeightUnit', 'Weight unit'),
        ]),
        ('Meteorite', [
            ('meteoriteType', 'Meteorite type'),
            ('meteoriteGroup', 'meteorite group'),
            ('chondriteAchondrite', 'Chondrite / achondrite'),
            ('meteoriteClass', 'Meteorite class'),
            ('petType', 'Petrology type'),
            ('petSubType', 'Petrology subtype'),
            ('recovery', 'Recovery'),
            ('recoveryDate', 'Recovery date'),
            ('recoveryWeight', 'Recovery weight'),
        ]),
        ('Botany', [
            ('exsiccati', 'Exsiccati'),
            ('exsiccatiNumber', 'Exsiccati number'),
            ('plantDescription', 'Plant description'),
            ('cultivated', 'Cultivated'),
            ('plantForm', 'Plant form'),
        ]),
        ('Silica gel', [
            ('populationCode', 'Population code'),
        ]),
        ('Nest', [
            ('nestShape', 'Nest shape'),
            ('nestSite', 'Nest site'),
        ]),
        ('Egg', [
            ('clutchSize', 'Clutch size'),
            ('setMark', 'Set mark'),
        ]),
        ('Parasite card', [
            ('barcode', 'Barcode'),
        ]),
        ('DNA Preparation', [
            ('extractionMethod', 'Extraction method'),
            ('resuspendedIn', 'Resuspended in'),
            ('totalVolume', 'Total volume')
        ]),
        ('Part', [
            ('partType', 'Part type')
        ]),
        ('Palaeontology', [
            ('catalogueDescription', 'Catalogue description'),
        ]),
        ('Related records', [
            ('relatedResourceID', 'Related resources'),
            ('partRefs', 'Parts'),
        ])
    ])

    def view(self, package_name, resource_id, record_id):

        """
        View an individual record
        :param id:
        :param resource_id:
        :param record_id:
        :return: html
        """

        self._load_data(package_name, resource_id, record_id)

        c.record_title = c.record_dict.get('occurrenceID')

        # Unpack the dynamic properties so they cna be used as just field values
        for prop in c.record_dict.pop('dynamicProperties').strip().split(';'):
            try:
                key, value = prop.strip().split('=')
            except ValueError:
                pass
            else:
                c.record_dict[key] = value

                print key, value

        # Remove self referential part refs
        try:
            if c.record_dict['partRefs'] == record_id:
                del c.record_dict['partRefs']
            # TODO: Remove part ref from list
        except KeyError:
            pass

        # Build an ordered dict for the field data
        # Organised into groups
        c.field_data = OrderedDict()

        collection_code = c.record_dict.get('collectionCode')

        collection_departments = {
            'BOT': 'Botany',
            'MIN': 'Mineralogy',
            'PAL': 'Paleontology',
            'ZOO': 'Zoology',
            'BMNH(E)': 'Entomology'
        }

        # TEMP: All should have this
        if collection_code:
            c.record_dict['collectionCode'] = '%s (%s)' % (collection_code, collection_departments[collection_code])

        # Parse collection date
        collection_date = list()
        # Loop through all the parts that make up the collectionDate
        for date_part in ['day', 'month', 'year']:
            # And pop them off the record_dict so they won't show up in the output
            date_part_value = c.record_dict.pop(date_part)
            # If we have a part value, add to the
            if date_part_value:
                collection_date.append(date_part_value)

        if collection_date:
            c.record_dict['year'] = '-'.join(collection_date)

        # Add registeredWeightUnit to registeredWeight
        try:
            c.record_dict['registeredWeight'] = '%s%s' % (c.record_dict['registeredWeight'], c.record_dict.pop('registeredWeightUnit'))
        except KeyError:
            # If the value doesn't exist in kwargs, we don't care, it won't get added to __dict__
            pass

        for group, fields in self.field_groups.items():

            field_values = OrderedDict()

            for field in fields:
                try:
                    value = c.record_dict.pop(field[0])
                except KeyError:
                    # If the value doesn't exist in kwargs, we don't care, it won't get added to the values
                    pass
                else:
                    if value:
                    # Key by label
                        field_values[field[1]] = value

            if field_values:
                c.field_data[group] = field_values

        return p.toolkit.render('record/specimen.html')





# TODO:

    #         {% if rec.relatedResourceID: %}
    #
    #     {% set rel_types = rec.relationshipOfResource.split(';') %}
    #     {% set related_records = {} %}
    #
    #     {% for rel_type in rel_types: %}
    #         {% do related_records.update({rel_type: []}) %}
    #     {% endfor %}
    #
    #     {% for i, id in enumerate(rec.relatedResourceID.split(';')): %}
    #         {% do related_records[rel_types[i]].append(id) %}
    #     {% endfor %}
    #
    #     <tr>
    #
    #         <tr><th colspan="3">Related records</th></tr>
    #
    #         {% for type, records in related_records.items(): %}
    #
    #             <tr>
    #                 <td><strong>{{ type|title }}</strong></td>
    #                 <td colspan="2">
    #                     <ul>
    #                         {% for record_id in records: %}
    #                             <li>
    #                                 {{ h.link_to(h.unique_identifier(record_id), h.url_for(controller='ckanext.nhm.controllers.record:RecordController', action='view', package_name=pkg.name, resource_id=res.id, record_id=record_id)) }}
    #                             </li>
    #                         {% endfor %}
    #                      </ul>
    #
    #                 </td>
    #             </tr>
    #
    #         {% endfor %}
    #
    #     </tr>
    #
    # {% endif %}
    #
    # {% if rec.associatedMedia: %}
    #
    #     {% for src in rec.associatedMedia.split(';'): %}
    #
    #         <img src="{{ src }}&width=100&height=100" />
    #
    #     {% endfor %}
    #
    # {% endif %}
    #
    #
    # {% set record_extent = h.get_record_point(rec) %}
    #
    # {% if record_extent %}
    #   {% snippet "snippets/record_map.html", extent=record_extent %}
    # {% endif %}