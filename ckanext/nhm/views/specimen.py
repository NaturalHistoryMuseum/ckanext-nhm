import logging
import re
import ckan.logic as logic
import ckan.plugins as p
from ckan.common import c
import json
from copy import deepcopy
import ckan.model as model
from pylons import config
from collections import OrderedDict
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.views.dwc import DarwinCoreView

log = logging.getLogger(__name__)

get_action = logic.get_action


class SpecimenView(DefaultView):
    """
    Controller for displaying a specimen record
    """
    resource_id = config.get("ckanext.nhm.specimen_resource_id")

    grid_default_columns = DarwinCoreView.grid_default_columns
    grid_column_widths = DarwinCoreView.grid_column_widths

    field_groups = OrderedDict([
        ("Classification", OrderedDict([
            ("scientificName", "Scientific name"),
            ("scientificNameAuthorship", "Author"),
            ("kingdom", "Kingdom"),
            ("phylum", "Phylum"),
            ("class", "Class"),
            ("order", "Order"),
            ("family", "Family"),
            ("genus", "Genus"),
            ("subgenus", "Subgenus"),
            ("specificEpithet", "Species"),
            ("infraspecificEpithet", "Subspecies"),
            ("higherClassification", "Higher classification"),
            ("taxonRank", "Taxon rank"),
        ])),
        ("Location", OrderedDict([
            ("labelLocality", "Label locality"),
            ("locality", "Locality"),
            ("stateProvince", "State province"),
            ("mine", "Mine"),
            ("miningDistrict", "Mining district"),
            ("viceCountry", "Vice country"),
            ("country", "Country"),
            ("continent", "Continent"),
            ("island", "Island"),
            ("islandGroup", "Island group"),
            ("waterBody", "Water body"),
            ("higherGeography", "Higher geography"),
            ("decimalLatitude", "Decimal latitude"),
            ("decimalLongitude", "Decimal longitude"),
            ("verbatimLatitude", "Verbatim latitude"),
            ("verbatimLongitude", "Verbatim longitude"),
            ("centroid", "Centroid"),
            ("maxError", "Max error"),
            ("geodeticDatum", "Geodetic datum"),
            ("georeferenceProtocol", "Georeference protocol"),
            ("minimumElevationInMeters", "Minimum elevation(m)"),
            ("maximumElevationInMeters", "Maximum elevation(m)"),
            ("minimumDepthInMeters", "Minimum depth(m)"),
            ("maximumDepthInMeters", "Maximum depth(m)"),
        ])),
        ("Collection event", OrderedDict([
            ("recordedBy", "Recorded by"),
            ("recordNumber", "Record number"),
            ("year", "Year"),
            ("month", "Month"),
            ("day", "Day"),
            ("eventTime", "Event time"),
            ("expedition", "Expedition"),
            ("habitat", "Habitat"),
        ])),
        ("Identification", OrderedDict([
            ("identifiedBy", "Identified by"),
            ("dateIdentified", "Date identified"),
            ("identificationQualifier", "Identification qualifier"),
            ("typeStatus", "Type status"),
            ("determinations", "Determinations"),
        ])),
        ("Specimen", OrderedDict([
            ("catalogNumber", "Catalogue number"),
            ("collectionCode", "Collection code"),
            ("subDepartment", "Sub department"),
            ("otherCatalogNumbers", "Other catalog numbers"),
            ("registrationCode", "Registration code"),
            ("kindOfObject", "Kind of object"),
            ("preparations", "Preparations"),
            ("preparationType", "Preparation type"),
            ("preservative", "Preservative"),
            ("collectionKind", "Collection kind"),
            ("collectionName", "Collection name"),
            ("donorName", "Donor name"),
            ("kindOfCollection", "Kind of collection"),
            ("observedWeight", "Observed weight"),
            ("individualCount", "Individual count"),
            ("sex", "Sex"),
            ("lifeStage", "Life stage"),
        ])),
        ("Mineralogy", OrderedDict([
            ("dateRegistered", "Date registered"),
            ("occurrence", "Occurrence"),
            ("commodity", "Commodity"),
            ("depositType", "Deposit type"),
            ("texture", "Texture"),
            ("identificationAsRegistered", "Identification as registered"),
            ("identificationDescription", "Identification description"),
            ("identificationVariety", "Identification variety"),
            ("identificationOther", "Identification other"),
            ("hostRock", "Host rock"),
            ("age", "Age"),
            ("ageType", "Age type"),
            ("geologyRegion", "Geology region"),
            ("mineralComplex", "Mineral complex"),
            ("tectonicProvince", "Tectonic province"),
            ("registeredWeight", "Registered weight"),
        ])),
        ("Stratigraphy", OrderedDict([
            ("earliestEonOrLowestEonothem", "Earliest eon/lowest eonothem"),
            ("latestEonOrHighestEonothem", "Latest eon/highest eonothem"),
            ("earliestEraOrLowestErathem", "Earliest era/lowest erathem"),
            ("latestEraOrHighestErathem", "Latest era/highest erathem"),
            ("earliestPeriodOrLowestSystem", "Earliest period/lowest system"),
            ("latestPeriodOrHighestSystem", "Latest period/highest system"),
            ("earliestEpochOrLowestSeries", "Earliest epoch/lowest series"),
            ("latestEpochOrHighestSeries", "Latest epoch/highest series"),
            ("earliestAgeOrLowestStage", "Earliest age/lowest stage"),
            ("latestAgeOrHighestStage", "Latest age/highest stage"),
            ("lowestBiostratigraphicZone", "Lowest biostratigraphic zone"),
            ("highestBiostratigraphicZone", "Highest biostratigraphic zone"),
            ("group", "Group"),
            ("formation", "Formation"),
            ("member", "Member"),
            ("bed", "Bed"),
            ("chronostratigraphy", "Chronostratigraphy"),
            ("lithostratigraphy", "Lithostratigraphy"),
        ])),
        ("Meteorites", OrderedDict([
            ("meteoriteType", "Meteorite type"),
            ("meteoriteGroup", "Meteorite group"),
            ("chondriteAchondrite", "Chondrite Achondrite"),
            ("meteoriteClass", "Meteorite class"),
            ("petrologyType", "Petrology type"),
            ("petrologySubtype", "Petrology subtype"),
            ("recovery", "Recovery"),
            ("recoveryDate", "Recovery date"),
            ("recoveryWeight", "Recovery weight"),
            # "Registered weight unit",  # Merged into Registered weight
        ])),
        ("Botany", OrderedDict([
            ("exsiccati", "Exsiccati"),
            ("exsiccatiNumber", "Exsiccati number"),
            ("plantDescription", "Plant description"),
            ("cultivated", "Cultivated"),
        ])),
        ("Zoology", OrderedDict([
            ("populationCode", "Population code"),
            ("nestShape", "Nest shape"),
            ("nestSite", "Nest site"),
            ("clutchSize", "Clutch size"),
            ("setMark", "Set mark"),
            ("barcode", "Barcode"),
            ("extractionMethod", "Extraction method"),
            ("resuspendedIn", "Resuspended in"),
            ("totalVolume", "Total volume"),
            ("partType", "Part type"),
        ])),
        ("Palaeontology", OrderedDict([
            ("catalogueDescription", "Catalogue description"),
        ])),
        ("Record", OrderedDict([
            ("occurrenceId", "Occurrence ID"),
            ("modified", "Modified"),
            ("created", "Created"),
            ("recordType", "Record type"),
        ])),
    ])

    def render_record(self, c):
        """
        Render a record
        Called from record controller, when viewing a record page
        @return: html
        """
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}

        occurrence_id = c.record_dict.get('occurrenceID')

        log.info('Viewing record %s', occurrence_id)

        c.record_title = c.record_dict.get('catalogNumber', None) or occurrence_id

        # Act on a deep copy of field groups, so deleting element will not have any impact
        c.field_groups = deepcopy(self.field_groups)

        # Some fields are being merged together - in which case we'll need custom filters
        # This can be set to bool false to not display a filter
        c.custom_filters = {}

        if c.record_dict.get('registeredWeight', None) and c.record_dict.get('registeredWeightUnit', None):
            # Create custom filter which acts on both weight and units
            c.custom_filters['registeredWeight'] = 'registeredWeight:%s|registeredWeightUnit:%s' % (c.record_dict['registeredWeight'], c.record_dict['registeredWeightUnit'])
            # Merge unit into the field
            c.record_dict['registeredWeight'] += ' %s' % c.record_dict['registeredWeightUnit']

        collection_date = []
        collection_date_filter = []

        # Merge day, month, year into one collection date field
        for k in ('day', 'month', 'year'):
            # Delete the exists field
            try:
                del c.field_groups['Collection event'][k]
            except KeyError:
                pass

            # Add to collection date field
            if c.record_dict.get(k, None):
                collection_date.append(c.record_dict.get(k))
                collection_date_filter.append('%s:%s' % (k, c.record_dict.get(k)))

        # Join the date for the record view
        c.record_dict['collectionDate'] = ' / '.join(collection_date)

        # Create a custom filter, so collection date filters on day, month and year
        c.custom_filters['collectionDate'] = '|'.join(collection_date_filter)

        c.field_groups['Collection event']['collectionDate'] = 'Collection date'

        # Some fields need stripping to remove empty string characters
        try:
            c.record_dict['maxError'] = c.record_dict['maxError'].strip()
        except AttributeError:
            pass

        c.determinations = {}
        c.determinations_count = 0

        if c.record_dict.get('determinations'):
            for det_type, det_value in json.loads(c.record_dict['determinations']).items():
                det_type = 'Filed as' if det_type == 'filedAs' else det_type.title()
                c.determinations[det_type] = det_value.split(';')
                # Want to use the largest number of determination value
                c.determinations_count = max(c.determinations_count, len(c.determinations[det_type]))

        # We do not want custom filters for determinations
        c.custom_filters['determinations'] = None

        # Related resources
        c.related_records = []

        related_resources = c.record_dict.get('relatedResourceID')

        if related_resources:
            related_resources = related_resources.split(';')

            try:
                related_resources.remove(occurrence_id)
            except ValueError:
                pass

            if related_resources:
                result = get_action('datastore_search')(
                    context,
                    {
                        'resource_id': c.resource['id'],
                        'filters': {'occurrenceID': related_resources},
                        'fields': ['_id', 'occurrenceID', 'catalogNumber']
                    }
                )

                for record in result['records']:
                    c.related_records.append({
                        '_id': record['_id'],
                        'title': 'Other part: %s' % (record['catalogNumber'] or record['occurrenceID']),
                    })

        for image in c.images:
            # Create a thumbnail image by replacing the max image dimensions we've located from KE EMu with thumbnail 100x100
            image['thumbnail'] = re.sub("width=[0-9]+&height=[0-9]+", "width=100&height=100", image['url'])

        return p.toolkit.render('record/specimen.html')

    def get_field_groups(self, resource):
        # Modify field groups for grid display
        field_groups = deepcopy(self.field_groups)
        # We do not want to show the record data in the grid or filters
        del field_groups['Record']
        return field_groups