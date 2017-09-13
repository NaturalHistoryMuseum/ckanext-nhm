import logging
import re
import json
import ckan.model as model
import ckan.logic as logic
import ckan.plugins as p
from copy import deepcopy
from ckan.plugins import toolkit as tk
from pylons import config
from collections import OrderedDict
from ckanext.nhm.views.default import DefaultView
from ckanext.nhm.views.dwc import DarwinCoreView

ValidationError = logic.ValidationError

log = logging.getLogger(__name__)

get_action = logic.get_action


class SpecimenView(DefaultView):
    """
    Controller for displaying a specimen record
    """
    resource_id = config.get("ckanext.nhm.specimen_resource_id")

    grid_default_columns = DarwinCoreView.grid_default_columns
    grid_column_widths = DarwinCoreView.grid_column_widths

    field_facets = [
        'collectionCode',
        'typeStatus',
        'family',
        'genus',
        'imageCategory',
        'gbifIssue'
    ]

    # Additional search filter options
    filter_options = {
        '_has_image': {
            'label': 'Has image',
            # 'sql': ('"{}"."associatedMedia" IS NOT NULL'.format(resource_id),),
            'solr': "_has_multimedia:true"
        },
        '_has_lat_long': {
            'label': 'Has lat/long',
            # BS: Changed to look for latitude field,as _geom is only available after a map has been added
            # As this works for all DwC, we might get datasets without a map
            # 'sql': ('"{}"."decimalLatitude" IS NOT NULL'.format(resource_id),),
            'solr': 'decimalLatitude:[* TO *]'
        },
        '_exclude_centroid': {
            'label': 'Exclude centroids',
            # 'sql': ('NOT (LOWER("{}"."centroid"::text) = ANY(\'{{true,yes,1}}\'))'.format(resource_id),),
            'solr': 'centroid:false'
        },
        '_exclude_mineralogy': {
            'label': 'Exclude Mineralogy',
            'hide': True,
            # 'sql': ('"{}"."collectionCode" <> \'MIN\''.format(resource_id),),
            'solr': '-collectionCode:MIN'
        }
    }

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
            ("vessel", "Vessel"),
            ("samplingProtocol", "Sampling protocol"),
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
            ("catalogueDescription", "Catalogue description"),
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
        ("Data Admin", OrderedDict([
            ("gbifIssue", "GBIF Error"),
            ("project", "Project"),
        ])),
        ("Record", OrderedDict([
            ("occurrenceID", "Occurrence ID"),
            ("modified", "Modified"),
            ("created", "Created"),
            ("recordType", "Record type")
        ])),
    ])

    def render_record(self, c):
        """
        Render a record
        Called from record controller, when viewing a record page
        @return: html
        """

        occurrence_id = c.record_dict.get('occurrenceID')

        log.info('Viewing record %s', occurrence_id)

        c.record_title = c.record_dict.get('catalogNumber', None) or occurrence_id

        # Act on a deep copy of field groups, so deleting element will not have any impact
        c.field_groups = deepcopy(self.field_groups)

        # We show the DQI at the top of the record page - so hide the group from
        # The actual record view - we need the group though for the filters
        del c.field_groups['Data Admin']

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

        # Parse determination names
        c.record_dict['determinations'] = {}
        c.record_dict['determination_labels'] = []

        for field in ['determinationNames', 'determinationTypes', 'determinationFiledAs']:

            label = field.replace('determination', '')
            # Add a space before capital letters
            label = re.sub(r"([A-Z])", r" \1", label)

            c.record_dict['determination_labels'].append(label)
            value = c.record_dict.get(field, None)
            try:
                c.record_dict['determinations'][label] = list(json.loads(value))
            except(ValueError, TypeError):
                if value:
                    c.record_dict['determinations'][label] = [value]
                else:
                    c.record_dict['determinations'][label] = []

        c.record_dict['determinations']['_len'] = max([len(l) for l in c.record_dict['determinations'].values()])

        # Set determinations to None if we don't have any values - required by the specimen template
        # to hide the Identification block
        if not c.record_dict['determinations']['_len']:
            c.record_dict['determinations']= None

        # No filters for determinations
        c.custom_filters['determinations'] = None

        # for image in c.images:
        #     # Create a thumbnail image by replacing preview with thumbnail
        #     image['thumbnail'] = image['href'].replace('preview', 'thumbnail')

        return p.toolkit.render('record/specimen.html')

    def get_field_groups(self, resource):
        # Modify field groups for grid display
        field_groups = deepcopy(self.field_groups)
        # We do not want to show the record data in the grid or filters
        del field_groups['Record']
        return field_groups

    def get_slickgrid_state(self):

        # Add the DQI column settings
        self.state['columnsTitle'].append(
            {
                'column': 'gbifIssue',
                'title': 'GBIF QI'
            }
        )

        self.state['columnsToolTip'].append(
            {
                'column': 'gbifIssue',
                'value': 'GBIF Data Quality Indicator'
            }
        )

        return self.state