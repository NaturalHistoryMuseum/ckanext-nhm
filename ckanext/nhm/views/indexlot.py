import ckan.logic as logic
import ckan.lib.base as base
import logging
from ckanext.nhm.views.default import DefaultView
from pylons import config
import ckan.plugins as p
from collections import OrderedDict

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action


class IndexLotView(DefaultView):
    """
    Controller for displaying a specimen record
    """

    resource_id = config.get("ckanext.nhm.indexlot_resource_id")

    field_facets = [
        'family',
        'type',
        'taxonRank',
        'imageCategory',
        'kindOfMaterial'
    ]

    # Additional search filter options
    filter_options = {
        '_has_image': {
            'label': 'Has images',
            'solr': "_has_multimedia:true"
        },
    }

    field_groups = OrderedDict([
        ("Classification", OrderedDict([
            ("currentScientificName", "Scientific name"),
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
        ("Specimen", OrderedDict([
            ("type", "Type"),
            ("media", "Media"),
            ("british", "British"),
        ])),
        ("Material details", OrderedDict([
            ("material", "Material"),
            ("kindOfMaterial", "Kind of material"),
            ("kindOfMedia", "Kind of media"),
            ("materialCount", "Count"),
            ("materialSex", "Sex"),
            ("materialStage", "Stage"),
            ("materialTypes", "Types"),
            ("materialPrimaryTypeNumber", "Primary type number"),
        ])),
        ("Record", OrderedDict([
            ("GUID", "GUID"),
            ("modified", "Modified"),
            ("created", "Created"),
        ])),
    ])

    def render_record(self, c):
        c.field_groups = self.field_groups
        return p.toolkit.render('record/collection.html')