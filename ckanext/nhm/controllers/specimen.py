from pylons import config
import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
from ckan.common import _, c
import logging
import re
from ckanext.nhm.controllers.record import RecordController
from ckanext.nhm.lib.helpers import get_department
import numpy as np
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
        ("Classification", [
            "Scientific name",
            "Scientific name authorship",
            "Kingdom",
            "Phylum",
            "Class",
            "Order",
            "Family",
            "Genus",
            "Subgenus",
            "Specific epithet",
            "Infraspecific epithet",
            "Higher classification",
            "Taxon rank",
        ]),
        ("Location", [
            "Label locality",
            "Locality",
            "State province",
            "Mine",
            "Mining district",
            "Vice country",
            "Country",
            "Continent",
            "Island",
            "Island group",
            "Water body",
            "Higher geography",
            "Decimal latitude",
            "Decimal longitude",
            "Verbatim latitude",
            "Verbatim longitude",
            "Centroid",
            "Max error",
            "Geodetic datum",
            "Georeference protocol",
            "Minimum elevation in meters",
            "Maximum elevation in meters",
            "Minimum depth in meters",
            "Maximum depth in meters",
        ]),
        ("Collection event", [
            "Recorded by",
            "Record number",
            "Collection date",
            # "Year", Merged into collection date
            # "Month", Merged into collection date
            # "Day", Merged into collection date
            "Event time",
            "Expedition",
            "Habitat",
        ]),
        ("Identification", [
            "Identified by",
            "Date identified",
            "Identification qualifier",
            "Type status",
            "Determinations"
        ]),
        ("Specimen", [
            "Catalog number",
            "Collection code",
            "Sub department",
            "Other catalog numbers",
            "Preparations",
            "Preparation type",
            "Preservative",
            "Collection kind",
            "Collection name",
            "Donor name",
            "Kind of collection",
            "Observed weight",
            "Individual count",
            "Sex",
            "Life stage",
        ]),
        ("Mineralogy", [
            "Date registered",
            "Occurrence",
            "Commodity",
            "Deposit type",
            "Texture",
            "Identification as registered",
            "Identification description",
            "Identification variety",
            "Identification other",
            "Host rock",
            "Age",
            "Age type",
            "Geology region",
            "Mineral complex",
            "Earliest eon or lowest eonothem",
            "Latest eon or highest eonothem",
            "Earliest era or lowest erathem",
            "Latest era or highest erathem",
            "Earliest period or lowest system",
            "Latest period or highest system",
            "Earliest epoch or lowest series",
            "Latest epoch or highest series",
            "Earliest age or lowest stage",
            "Latest age or highest stage",
            "Lowest biostratigraphic zone",
            "Highest biostratigraphic zone",
            "Group",
            "Formation",
            "Member",
            "Bed",
            "Chronostratigraphy",
            "Lithostratigraphy",
            "Tectonic province",
            "Registered weight",
            # "Registered weight unit",  # Merged into Registered weight
        ]),
        ("Meteorite", [
            "Meteorite type",
            "Meteorite group",
            "Chondrite achondrite",
            "Meteorite class",
            "Petrology type",
            "Petrology subtype",
            "Recovery",
            "Recovery date",
            "Recovery weight",
        ]),
        ("Botany", [
            "Exsiccati",
            "Exsiccati number",
            "Plant description",
            "Cultivated",
        ]),
        ("Silica gel", [
            "Population code",
        ]),
        ("Nest", [
            "Nest shape",
            "Nest site",
        ]),
        ("Egg", [
            "Clutch size",
            "Set mark",
        ]),
        ("Parasite card", [
            "Barcode",
        ]),
        ("DNA Preparation", [
            "Extraction method",
            "Resuspended in",
            "Total volume",
        ]),
        ("Part", [
            "Part type",
        ]),
        ("Palaeontology", [
            "Catalogue description",
        ]),
        ("Record", [
            "Occurrence ID",
            "Modified",
            "Created",
            "Record type",
            "Registration code",
            "Kind of object",
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

        occurrence_id = c.record_dict.get('Occurrence ID')

        log.info('Viewing record %s', occurrence_id)

        c.record_title = c.record_dict.get('Catalog number', None) or occurrence_id

        c.field_groups = self.field_groups

        # Some fields are being merged together - in which case we'll need custom filters
        # This can be set to bool false to not display a filter
        c.custom_filters = {}

        if c.record_dict.get('Registered weight', None) and c.record_dict.get('Registered weight unit', None):
            # Create custom filter which acts on both weight and units
            c.custom_filters['Registered weight'] = 'Registered weight:%s|Registered weight unit:%s' % (c.record_dict['Registered weight'], c.record_dict['Registered weight unit'])
            # Merge unit into the field
            c.record_dict['Registered weight'] += ' %s' % c.record_dict['Registered weight unit']

        #  Build a sub dictionary of parts to use in collection date
        collection_date = OrderedDict((k, c.record_dict[k]) for k in ('Day', 'Month', 'Year') if c.record_dict.get(k, None))

        # Join the date for the record view
        c.record_dict['Collection date'] = ' / '.join(collection_date.values())

        # Create a custom filter, so collection date filters on day, month and year
        c.custom_filters['Collection date'] = '|'.join(['%s:%s' % (k, v) for k, v in collection_date.iteritems()])

        # Some fields need stripping to remove empty string characters
        try:
            c.record_dict['Max error'] = c.record_dict['Max error'].strip()
        except AttributeError:
            pass

        # Pattern for matching key in determination date
        regex = re.compile('^([a-z ]+)=(.*)', re.IGNORECASE)
        determinations = []

        # Parse the determinations string
        for determination in c.record_dict['Determinations'].split('|'):
            result = regex.match(determination)
            try:
                determinations.append([result.group(1)] + result.group(2).split(';'))
            except AttributeError:
                pass

        if determinations:
            # Transpose list of determinations & fill in missing values so they are all the same length
            c.record_dict['Determinations'] = map(lambda *row: list(row), *determinations)
            # We do not want custom filters for determinations
            c.custom_filters['Determinations'] = None
        else:
            c.record_dict['Determinations'] = None

        # Related resources
        c.related_records = []

        related_resources = c.record_dict.get('Related resource ID').split(';')

        try:
            related_resources.remove(occurrence_id)
        except ValueError:
            pass

        if related_resources:
            result = get_action('datastore_search')(
                self.context,
                    {
                        'resource_id': resource_id,
                        'filters': {'Occurrence ID': related_resources},
                        'fields': ['_id', 'Occurrence ID', 'Catalog number']
                    }
            )

            for record in result['records']:
                c.related_records.append({
                    '_id': record['_id'],
                    'title': 'Part: %s' % (record['Catalog number'] or record['Occurrence ID']),
                })

        for image in c.images:
            # Create a thumbnail image by replacing the max image dimensions we've located from KE EMu with thumbnail 100x100
            image['thumbnail'] = re.sub("width=[0-9]+&height=[0-9]+", "width=100&height=100", image['url'])

        return p.toolkit.render('record/specimen.html')