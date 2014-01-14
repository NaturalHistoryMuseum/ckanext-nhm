import pylons
import ckan.lib.base as base
import ckan.plugins as p
from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.lib.render import find_template
from sqlalchemy.orm.exc import NoResultFound
from ckanext.nhm.db import _get_engine, _make_session
from ckanext.nhm.model.keemu import *
from ckanext.nhm.controllers.record import RecordController
from sqlalchemy.orm import class_mapper, RelationshipProperty as SQLAlchemyRelationshipProperty

import logging

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

class KeEMuRecordController(RecordController):
    """
    Controller for displaying KE EMu records
    """
    def view(self, id, resource_id, record_id):
        """
        Default record view
        @param id: dataset name string
        @param resource_id: id uuid
        @param record_id: int (irn)
        """

        # This checks resources exist correctly

        # Get the datastore record - checks the dataset, resource and record exists in the resource
        datastore_record = self._load_record(id, resource_id, record_id)

        if not datastore_record:
            abort(404, _('Record not found'))

        # Get the keemu record
        c.record = self._load_keemu_record(record_id)

        # Use a dict comprehension to build the template record
        # This also lazy loads any child properties

        c.record_dict = OrderedDict()
        c.record_dict['class_fields'] = OrderedDict()
        c.record_dict['class_relationship_fields'] = OrderedDict()
        c.record_dict['associated_specimens'] = OrderedDict()
        c.record_dict['irn'] = c.record.irn

        # Process stratigraphy - get the stratigraphy units
        if hasattr(c.record, 'stratigraphy'):

            # Build an array holding the stratigraphy data
            c.record_dict['stratigraphy_units'] = OrderedDict()

            # Build a list of stratigraphic groups
            stratigraphic_groups = {}

            for stratigraphic_group, unit_types in STRATIGRAPHIC_UNIT_TYPES.items():

                for unit_type in unit_types:
                    # Remove first three chars of unit type: Lit, Chr etc.,
                    unit_type = unit_type[3:].lower()
                    stratigraphic_groups[unit_type] = stratigraphic_group

            # Populate with the data
            for stratigraphy_unit in c.record.stratigraphy.stratigraphic_unit:

                group = stratigraphic_groups[stratigraphy_unit.type]

                if group not in c.record_dict['stratigraphy_units']:
                    c.record_dict['stratigraphy_units'][group] = OrderedDict()

                try:
                    c.record_dict['stratigraphy_units'][group][stratigraphy_unit.type][stratigraphy_unit.direction] = stratigraphy_unit.unit.name
                except KeyError:
                    c.record_dict['stratigraphy_units'][group][stratigraphy_unit.type] = {stratigraphy_unit.direction : stratigraphy_unit.unit.name}

        # Loop through every property processing it
        # If it's fields not included in the core catalogue & specimen class
        # Add them to the class_fields property
        for prop in class_mapper(c.record.__class__).iterate_properties:

            # Flag for being a relationship field
            is_relationship = False

            # Skip if we've already processed
            if prop.key in c.record_dict:
                continue

            value = getattr(c.record, prop.key, None)

            # Skip foreign keys
            if type(prop) in (RelationshipProperty, SQLAlchemyRelationshipProperty):

                is_relationship = True

                if value:

                    value_list = value if isinstance(value, list) else [value]

                    # TODO: same as import. Need to put this somewhere. Toolkit?
                    for i, rec in enumerate(value_list):

                        # Is this a stub? If it is, we don't want it
                        # TODO: Check this works
                        if rec == StubModel:
                            del value_list[i]

                        # Is this a link to another specimen?
                        # If it is, add it to the associated specimens list
                        if SpecimenModel in rec.__class__.__mro__:

                            try:
                                c.record_dict['associated_specimens'][prop.key].append(rec)
                            except KeyError:
                                c.record_dict['associated_specimens'][prop.key] = [rec]

                            del value_list[i]

                    # If all items have been processed (all Stubs or Specimens), we do not want to do anything more with this property
                    if not value_list:
                        continue

            else:

                # We want to ignore foreign key fields - these will be handled in relationships
                if prop.columns[0].foreign_keys:
                    continue

            # Are these core fields
            if (prop.parent.class_ == CatalogueModel) or (prop.parent.class_.__bases__[0] == CatalogueModel):
                c.record_dict[prop.key] = value
            else:
                label = prop.key.replace('_', ' ').capitalize()
                if is_relationship:
                    c.record_dict['class_relationship_fields'][prop.key] = value
                else:
                    c.record_dict['class_fields'][label] = value

        c.record_dict['date_identified'] = ''
        for d in ['date_identified_year', 'date_identified_month', 'date_identified_day']:
            try:

                if c.record_dict[d]:
                    c.record_dict['date_identified'] = '%s %s' % (c.record_dict[d], c.record_dict['date_identified'])
                else:
                    break
            except KeyError:
                break

        # Build template candidate files
        candidate_template_files = []

        for cls in c.record.__class__.__mro__:

            # Don't go deeper than CatalogueModel
            if cls == CatalogueModel:
                break

            candidate_template_file = "keemu-record/%s.html" % cls.__name__.replace("Model", "").lower()
            candidate_template_files.append(candidate_template_file)

        for template_file in candidate_template_files:
            # If the file exists, exit loop
            if find_template(template_file):
                break

        return p.toolkit.render(template_file)


    def view_dwc(id, resource_id, record_id):
        """
        View the record as DwC
        @param id: dataset name string
        @param resource_id: id uuid
        @param record_id: int (irn)
        """
        pass

    def _load_keemu_record(self, record_id):
        # Create a session to the KE EMu database
        data_dict = {'connection_url': pylons.config['ckan.datastore.write_url']}
        engine = _get_engine(data_dict)
        session = _make_session(engine)

        try:
            return session.query(CatalogueModel).with_polymorphic('*').filter(CatalogueModel.irn == record_id).one()
        except NoResultFound:
            abort(404, _('Record not found'))



