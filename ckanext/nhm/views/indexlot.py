import ckan.logic as logic
import ckan.lib.base as base
import logging
from ckanext.nhm.views.default import DefaultView
from pylons import config
import ckan.plugins as p

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

    def render_record(self, c):
        return p.toolkit.render('record/indexlot.html')

    field_facets = [
        'Family',
        'taxonRank',
        'imageCategory',
        'kindOfMaterial'
    ]

    # Additional search filter options
    filter_options = {
        '_has_image': {
            'label': 'Has image',
            'solr': "_has_multimedia:true"
        },
    }

# def indexlot_material_details(record_dict):
#     """
#     Parse the material details into an array, with first column the header
#     @param record_dict:
#     @return:
#     """
#
#     material_details = []
#
#     material_detail_fields = [
#         'Material count',
#         'Material sex',
#         'Material stage',
#         'Material types',
#         'Material primary type no'
#     ]
#
#     # Create a list of lists, containing field and values
#     # First row will be field title
#     for material_detail_field in material_detail_fields:
#         if record_dict[material_detail_field]:
#             field_values = record_dict[material_detail_field].split(';')
#             if field_values:
#                 label = material_detail_field.replace('Material', '').strip().capitalize()
#                 material_details.append([label] + field_values)
#
#     # Transpose list of values & fill in missing values so they are all the same length
#     if material_details:
#         material_details = map(lambda *row: list(row), *material_details)
#
#     return material_details

