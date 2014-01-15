import re
import ckan.model as model
import ckan.logic as logic
import ckan.lib.cli as cli
import ckan
import os

import ConfigParser

import sqlalchemy
import pylons
import logging

from sqlalchemy.orm import class_mapper
from sqlalchemy import and_, UniqueConstraint, String
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import ProgrammingError, DataError
from sqlalchemy.schema import CreateSchema

from keparser import KEParser
from ckanext.nhm.model.keemu import *
from datetime import datetime
from ckanext.nhm.db import _get_engine, _make_session
from ckanext.nhm.lib.helpers import ensure_list

log = logging.getLogger(__name__)

# Regex for extracting year,month,day from PalDetDate
re_date = re.compile('^([0-9]{4})-?([0-9]{2})?-?([0-9]{2})?')
# Regular expression for finding model name
re_model = re.compile('[a-zA-Z &]+')

class KEEMuImportException(Exception):
    pass


class KEEMuImportCommand(cli.CkanCommand):
    '''
    Commands:
        paster keemu import-taxonomy -c <config>
        paster keemu import-catalogue -c /var/www/data.nhm/development.ini

    Where:
        <config> = path to your ckan config file

    The commands should be run from the ckanext-nhm directory.
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    counter = 0

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print KEEMuImportCommand.__doc__
            return

        cmd = self.args[0]

        self.method = cmd.replace('-', '_')

        # Need to call _load_config() before running
        self._load_config()

        if self.method.startswith('_'):
            log.error('Cannot call private command %s' % (self.method,))
            return

        # Set up API context
        user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        self.context = {'model': model, 'session': model.Session, 'user': user['name'], 'extras_as_string': True}

        # Set up datastore DB engine & session
        # Changed from using separate KE EMu DB connection - now uses schema
        self.datastore_db_engine = _get_engine({'connection_url': pylons.config['ckan.datastore.write_url']})
        self.datastore_db_session = _make_session(self.datastore_db_engine)

        # Try and call the method, if it exists
        if hasattr(self, self.method):
            start_time = datetime.now()
            getattr(self, self.method)()
            log.info('Runtime: %s', datetime.now() - start_time)
        else:
            log.error('Command %s not recognized' % (self.method,))


    def build_dataset(self):
        """
        Build the dataset & resource views
        This should run after the import scripts have run
        """

        keemu_dataset_name = pylons.config['nhm.keemu_dataset_name']

        views_config = ConfigParser.ConfigParser()
        views_config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'keemu_datasets.ini'))

        try:

            dataset = logic.get_action('package_show')(self.context, {'id': keemu_dataset_name})

        except logic.NotFound:

            # If dataset doesn't exists, create it

            # Error adds dataset_show to __auth_audit: remove it
            self.context['__auth_audit'] = []

            log.info('Creating dataset & resources.')

            # TODO: More metadata. Create date etc.,
            # TODO: Read file produced date

            dataset_params = {
                'author': None,
                'author_email': None,
                'license_id': u'other-open',
                'maintainer': None,
                'maintainer_email': None,
                'name': keemu_dataset_name,
                'notes': u'Specimen records from the Natural History Museum\'s catalogue',
                'resources': [],
                'title': "Specimen catalogue",
            }

            try:
                # Create the dataset
                dataset = logic.get_action('package_create')(self.context, dataset_params)
            except Exception:
                raise

        except ProgrammingError, e:
            raise

        # Build a temporary table of determinations, which uses part's and egg's parents

        # Drop and create
        self.datastore_db_engine.execute(sqlalchemy.text('DROP TABLE IF EXISTS tmp_determination'.format(schema=KEEMU_SCHEMA)))
        self.datastore_db_engine.execute(sqlalchemy.text('CREATE TEMP TABLE tmp_determination '
                                                         'AS '
                                                            '(SELECT DISTINCT ON(d.specimen_irn) specimen_irn, taxonomy_irn '
                                                            'FROM {schema}.determination d '
                                                            'INNER JOIN {schema}.specimen s ON s.irn = d.specimen_irn ORDER BY d.specimen_irn, filed_as DESC) '
                                                         'UNION '
                                                            '(SELECT DISTINCT ON(s.irn) s.irn as specimen_irn, taxonomy_irn '
                                                            'FROM {schema}.SPECIMEN s '
                                                            'INNER JOIN {schema}.part p ON p.irn = s.irn '
                                                            'INNER JOIN {schema}.determination d ON p.parent_irn = d.specimen_irn '
                                                            'WHERE NOT EXISTS (SELECT 1 FROM {schema}.determination WHERE specimen_irn = s.irn) '
                                                            'ORDER BY s.irn, filed_as DESC) '
                                                        'UNION '
                                                            '(SELECT DISTINCT ON(s.irn) s.irn as specimen_irn, taxonomy_irn '
                                                            'FROM {schema}.specimen s '
                                                            'INNER JOIN {schema}.egg e ON e.irn = s.irn '
                                                            'INNER JOIN {schema}.determination d ON e.parent_irn = d.specimen_irn '
                                                            'WHERE NOT EXISTS (SELECT 1 FROM {schema}.determination WHERE specimen_irn = s.irn) '
                                                            'ORDER BY s.irn, filed_as DESC)'.format(schema=KEEMU_SCHEMA)))


        # Get all existing resources keyed by name
        existing_resources = {r['name']: r for r in dataset['resources']}

        # Loop through
        for resource_name in views_config.sections():

            try:

                resource_id = existing_resources[resource_name]['id']

            except KeyError:  # We don't have a datastore resource so create one

                log.info('Creating datastore %s.' % resource_name)

                datastore_params = {
                    'records': [],
                    'resource': {
                        'package_id': dataset['id'],
                        'name': resource_name,
                        'description': views_config.get(resource_name, 'description'),
                    }
                }

                datastore = logic.get_action('datastore_create')(self.context, datastore_params)
                resource_id = datastore['resource_id']

            else:

                # Resource already exists - need to update last modified date
                resource = existing_resources[resource_name]
                resource['last_modified'] = datetime.now()
                logic.get_action('resource_update')(self.context, resource)

            finally:

                # Delete & recreate the tables, building them from the ME EMu source tables
                log.info('Rebuilding views %s.' % resource_name)

                # Delete the existing table (in the datastore)
                delete_sql = sqlalchemy.text(u'DROP TABLE IF EXISTS "%s"' % resource_id)
                self.datastore_db_engine.execute(delete_sql)

                # And recreate the table
                select_sql = views_config.get(resource_name, 'sql').format(schema=KEEMU_SCHEMA)
                create_sql = sqlalchemy.text('CREATE TABLE "{id}" AS {select_sql}'.format(id=resource_id, select_sql=select_sql))
                self.datastore_db_engine.execute(create_sql)

    def create_schema(self):

        # Create the database tables for catalogue
        log.info('Creating catalogue schema')

        datastore_write_url = cli.parse_db_config('ckan.datastore.write_url')

        # Create the actual DB schema if it doesn't already exist
        # CREATE SCHEMA IF NOT EXISTS is PG 9.3
        result = self.datastore_db_engine.execute(sqlalchemy.text(u'SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'%s\')' % KEEMU_SCHEMA))

        if not result.scalar():
            self.datastore_db_engine.execute(sqlalchemy.text(u'CREATE SCHEMA %s AUTHORIZATION %s' % (KEEMU_SCHEMA, datastore_write_url['db_user'])))
        #
        # # Grant read access to the datastore_read_url user
        # #datastore_read_url = cli.parse_db_config('ckan.datastore.read_url')
        #
        # # TODO: Only working if run in DB. Need to fix
        # #self.datastore_db_engine.execute(sqlalchemy.text(u'GRANT USAGE ON SCHEMA %s TO %s' % (KEEMU_SCHEMA, datastore_read_url['db_user'])))
        # #self.datastore_db_engine.execute(sqlalchemy.text(u'GRANT SELECT ON ALL TABLES IN SCHEMA %s TO %s' % (KEEMU_SCHEMA, datastore_read_url['db_user'])))
        #
        # # And create the tables
        # Base.metadata.create_all(self.datastore_db_engine)

    def _parse_keemu(self, import_file):
        """
        Helper function for creating Keemu Parser
        :param import_file:
        :return:
        """
        import_file_path = os.path.join(pylons.config['nhm.keemu_export_dir'], import_file)

        try:
            # TODO: Keep note of what files have been imported
            return KEParser(import_file_path, pylons.config['nhm.keemu_schema'])
        except IOError, e:
            log.error(e)
            return []

    def _get_catalogue_model_class(self, data):

        model_class = None

        # If it doesn't even have a record type, what's the point of keeping it?
        if not 'ColRecordType' in data:
            log.debug('Skipping record %s: No record type', data['irn'])
            return None

        # Build an array of potential candidate classes
        candidate_classes = []

        collection = data['ColKind'] if 'ColKind' in data else None
        collection_department = data['ColDepartment'] if 'ColDepartment' in data else None

        matches = re_model.match(data['ColRecordType'])

        if matches:
            cls = matches.group(0).replace(' ', '')

            if collection:
                # Add candidate class based on ColKind (used for mineralogy) MeteoritesSpecimenModel
                candidate_classes.append('{0}{1}Model'.format(data['ColKind'], cls))

            if collection_department:
                # Add candidate class BotanySpecimenModel
                candidate_classes.append('{0}{1}Model'.format(collection_department, cls))

            # Add candidate class SpecimenModel, ArtefactModel
            candidate_classes.append('{0}Model'.format(cls))

        for candidate_class in candidate_classes:
            if candidate_class in globals():
                # Do we have a model class for this candidate
                model_class = globals()[candidate_class]
                break

        return model_class

    def import_taxonomy(self):
        self._import(import_file_name='etaxonomy', model_class=TaxonomyModel)

    def import_multimedia(self):
        self._import(import_file_name='emultimedia', model_class=MultimediaModel)

    def import_stratigraphy(self):
        self._import(import_file_name='enhmstratigraphy', model_class=StratigraphyModel)

    def import_site(self):
        self._import(import_file_name='esites', model_class=SiteModel)

    def import_collection_event(self):
        self._import(import_file_name='ecollectionevents', model_class=CollectionEventModel)

    def import_catalogue(self):
        self._import(import_file_name='ecatalogue', model_class_callback=self._get_catalogue_model_class)

    def _import(self, import_file_name, model_class=None, model_class_callback=None):

        self.create_schema()

        import_file_name += '.export.20131205.gz'
        # import_file_name += '.export'

        keemu_data = self._parse_keemu(import_file_name)

        for data in keemu_data:

            # Output status (needs to go at top so outputs even for skipped records)
            self._log_status(keemu_data)

            if model_class_callback:
                model_class = model_class_callback(data)

            # If we don't have a model class, continue to next record
            if not model_class:
                log.debug('Skipping record %s: No model class for %s', data['irn'], data.get('ColRecordType', 'No record type'))
                continue

            log.debug('Processing %s record %s', model_class.__name__.replace('Model', '').lower(), data['irn'])

            # Try and call data processing method.
            # Only required if there's extra data processing needed so fail without error
            try:
                preprocessor_func = '_{0}_preprocessor'.format(self.method)
                getattr(self, preprocessor_func)(model_class, data)
            except AttributeError:
                pass
            except KEEMuImportException:
                # If the preprocessor function returns DataProcessorException, continue to next record
                continue

            try:

                # Do we already have a record for this?
                record = self.datastore_db_session.query(CatalogueModel).filter_by(irn=data.get('irn')).one()

                # Is this a stub record? If it is, we want to change the type and reload.
                # Seems a bit of a hack, but SQLAlchemy does not have a simple way of modifying the type
                if isinstance(record, StubModel):

                    polymorphic_type = model_class.__mapper_args__['polymorphic_identity']
                    # Manually set type
                    self.datastore_db_session.execute('UPDATE %s.catalogue SET type=:type WHERE irn=:irn' % KEEMU_SCHEMA, {'type': polymorphic_type, 'irn': data.get('irn')})

                    # If this has a child table, insert the IRN so updates will work
                    if model_class.__mapper__.local_table.name != 'specimen':
                        # And create empty row in the polymorphic table
                        self.datastore_db_session.execute('INSERT INTO %s.%s (irn) VALUES (:irn)' % (KEEMU_SCHEMA, model_class.__mapper__.local_table.name), {'irn': data.get('irn')})

                    # Commit & expunge so the item can be reloaded
                    self.datastore_db_session.commit()
                    self.datastore_db_session.expunge(record)
                    record = self.datastore_db_session.query(CatalogueModel).filter_by(irn=data.get('irn')).one()

                # Process the relationships
                data = self._process_relationships(model_class, data, record)

                # Populate the data
                record.rebuild(**data)

            except NoResultFound:

                data = self._process_relationships(model_class, data)
                # Create a new record
                record = model_class(**data)

            try:

                self.datastore_db_session.merge(record)
                self.datastore_db_session.commit()

            except DataError, e:
                # Save this error to the log - will need to follow up on these
                log.critical('DB DataError: record %s not created.' % data['irn'], {'data': data}, exc_info=e)

    def process_errors(self):
        pass
        # Get all errors
        # TODO: Fix this
        #for error in model.Session.query(Log).filter_by(logger=log.name).all():
        #    print error.args
        #    print error.trace


    def _process_relationships(self, model_class, data, record=None):

        # Basic relationship handling.

        # More complex scenarios are handled in the individual processing functions
        for prop in class_mapper(model_class).iterate_properties:

            # Skip the field if the property key is already set in the data object
            # The field has been set in the import types custom preprocess function

            if prop.key in data:
                continue

            # Is this a relationship property?
            # NB: This excludes backrefs, which will be using sqlalchemy.orm.properties.RelationshipProperty, not our own
            if type(prop) == RelationshipProperty:

                # Try and find a child model to use for this relationship
                try:
                    child_model = prop.mapper.class_
                    # If the child model has irn primary key, it relates to a KE EMu record
                    # And a simple relationship should be used
                    if child_model.__mapper__.primary_key[0].key == 'irn':
                        child_model = None

                except AttributeError:
                    child_model = None

                # This is a relationship to a secondary object like SexStage
                if child_model:

                    # If unique, we'll try loading the values from the database first
                    # And only create if they don't exist
                    unique = False

                    for constraint in child_model.__table__.constraints:
                        if constraint.__class__ == UniqueConstraint:
                            unique = True
                            break

                    fields = {}

                    for column in child_model.__table__.columns:
                        if column.alias:
                            for alias in ensure_list(column.alias):
                                fields[alias] = column.key

                    # Populate a list of fields
                    data_fields = self._populate_subfield_data(fields.keys(), data)

                    # If we have data retrieve / create a model record
                    if data_fields:
                        data[prop.key] = []
                        # Loop through all the list of fields
                        for field_list in data_fields:

                            # Sometimes nothing is populated - for example, EntSexSex just has None
                            # We want to skip these
                            if not [x for x in field_list.values() if x is not None]:
                                continue

                            if unique:
                                # Try and get record from database
                                try:

                                    filters = []
                                    for alias, key in fields.items():
                                        # Build the filters
                                        col = getattr(child_model, key)

                                        # Do we have a value for this field
                                        if alias not in field_list:
                                            field_list[alias] = None

                                        # String fields should always be lower case & '' for null to ensure unique constraints work correctly
                                        if isinstance(child_model.__table__.columns[key].type, String):
                                            try:
                                                field_list[alias].lower()
                                            except AttributeError:
                                                field_list[alias] = ''

                                        filters.append(col.__eq__(field_list[alias]))

                                    # Run the query
                                    data[prop.key].append(self.datastore_db_session.query(child_model).filter(and_(*filters)).one())

                                except NoResultFound:
                                    # Not found, create a new one
                                    data[prop.key].append(child_model(**field_list))

                            elif 'delete-orphan' in prop.cascade:
                                # If this property has a delete-orphan cascade, everything's fine
                                # SQLa will handle updates, removing old records
                                # But for non unique / no delete orphan relationships
                                # This code will create duplicate records in the associated table
                                # Not a problem now, but throw an exception in case it ever happens
                                data[prop.key].append(child_model(**field_list))
                            else:

                                raise KEEMuImportException('Non-unique relationship used in %s.', prop.key)

                else:

                    # Basic relationship, in the format:
                    # stratigraphy = relationship("StratigraphyModel", secondary=collection_event_stratigraphy, alias='GeoStratigraphyRef')
                    field_names = prop.alias
                    irns = []

                    # Ensure it's a list
                    field_names = ensure_list(field_names)

                    for field_name in field_names:
                        value = data.get(field_name)
                        if value:
                            irns += ensure_list(value)

                    # Dedupe IRNS & ensure we are not linking to the same record - eg: 687077
                    try:
                        irns = list(set(irns))
                        irns.remove(data['irn'])
                    except ValueError:
                        pass

                    # Do we have any IRNs?
                    if irns:

                        # Get the relationship model class
                        relationship_model = prop.argument()

                        # Load the model objects and assign to the property
                        data[prop.key] = self.datastore_db_session.query(relationship_model).filter(relationship_model.irn.in_(irns)).all()
                        existing_irns = [record.irn for record in data[prop.key]]

                        # Do we have any missing IRNs
                        missing_irns = list(set(irns) - set(existing_irns))

                        if missing_irns:

                            # Is this a property we want to create stub records for
                            if prop.key == 'associated_record':
                                for missing_irn in missing_irns:
                                    data[prop.key].append(StubModel(irn=missing_irn))
                            else:
                                log.error('Missing IRN %s in relationship %s(%s).%s', ','.join(str(x) for x in missing_irns), model_class.__name__, data['irn'], prop.key)

            # This isn't a relationship property - but perform check to see if this a foreign key field
            else:

                try:

                    column = prop.columns[0]

                    foreign_key = column.foreign_keys.pop()
                    # Add the foreign key back
                    column.foreign_keys.add(foreign_key)
                    foreign_key_value = None

                    # Loop through aliases / key and see if we have a foreign key value
                    candidate_names = column.alias if column.alias else prop.key
                    candidate_names = ensure_list(candidate_names)

                    for candidate_name in candidate_names:
                        foreign_key_value = data.get(candidate_name)
                        if foreign_key_value:
                            break

                    # We do have a foreign key value, so now perform check to see if it exists
                    if foreign_key_value and isinstance(foreign_key_value, int):

                        result = self.datastore_db_session.execute("SELECT COUNT(*) as exists FROM %s WHERE %s = :foreign_key_value" % (foreign_key.column.table, foreign_key.column.name), {'foreign_key_value': foreign_key_value})
                        record = result.fetchone()

                        if not record.exists:
                            # If the record doesn't exist, create a stub for part parents
                            if prop.key == 'parent_irn':
                                self.datastore_db_session.add(StubModel(irn=foreign_key_value))
                            else:
                            # Otherwise, delete the property so it is not used
                            # Need to ensure all candidate names are unset
                                for candidate_name in candidate_names:
                                    try:
                                        del data[candidate_name]
                                    except KeyError:
                                        pass

                                log.error('%s(%s): Missing foreign key %s for %s field. Field removed from record.', model_class.__name__, data['irn'], foreign_key_value, prop.key)

                except (AttributeError, KeyError):
                    pass


        return data

    def _import_stratigraphy_preprocessor(self, model_class, data):

        # Helper function to get the value of a field
        def _get_field_value():
            field_name = '{0}{1}'.format(unit_type, direction)
            field_value = data.get(field_name)
            # We don't want to give the entire stratigraphic history
            # We just want the current data - so use the first item
            # This affects only 298 records
            if isinstance(field_value, list):
                field_value = field_value[0]

            return field_value

        unit_names = []
        # Loop through all of the period types, see if its set in data
        # If it is and we don't already have it, add to period_names

        for group in STRATIGRAPHIC_UNIT_TYPES.values():
            for unit_type in group:
                # Every unit type has To & From: ChrEonTo & ChrEonFrom
                for direction in ['To', 'From']:
                    value = _get_field_value()
                    # Do we have a value?
                    if value and value not in unit_names:
                        unit_names.append(value)

        if unit_names:
            data['stratigraphic_unit'] = []
            try:
                unit_models = self._get_stratigraphic_unit_model_by_names(unit_names)
            except ProgrammingError, e:
                print data['irn']
                raise e

            # Now loop through all the types, assigning the unit model
            for group in STRATIGRAPHIC_UNIT_TYPES.values():
                for unit_type in group:
                    for direction in ['To', 'From']:
                        value = _get_field_value()

                        if value:
                            unit_model = unit_models[unicode(value)]
                            # First three chars of unit type aren't useful: Lit, Chr etc.,
                            unit_type = unit_type[3:].lower()
                            data['stratigraphic_unit'].append(StratigraphicUnitAssociation(stratigraphy_irn=data['irn'], unit_id=unit_model.id, type=unit_type, direction=direction.lower()))

        return data

    def _get_stratigraphic_unit_model_by_names(self, unit_names):

        unit_models = {}
        results = self.datastore_db_session.query(StratigraphicUnitModel).filter(StratigraphicUnitModel.name.in_(unit_names)).all()

        for unit_model in results:
            unit_models[unicode(unit_model.name)] = unit_model

        # De we have any new unit models? If so, we need to create them
        missing_unit_names = list(set(unit_names) - set(unit_models.keys()))

        if missing_unit_names:

            for missing_unit_name in missing_unit_names:
                # log.warning('Creating stratigraphic unit %s', missing_unit_name)
                self.datastore_db_session.add(StratigraphicUnitModel(name=missing_unit_name))

            self.datastore_db_session.commit()

            # WARNING: this function calls itself after the cache has been cleared
            # To rebuild the periods. Possible recursion
            unit_models = self._get_stratigraphic_unit_model_by_names(unit_names)

        return unit_models

    def _import_multimedia_preprocessor(self, model_class, data):
        # Ke Emu has mime_types:  application, message, video, x-url, text, image
        # Application (including ms word) has stuff we definitely don't want released - messages & text possible risk too
        # If it's not an image or video, skip it
        if data.get('MulMimeType', None) not in ('image', 'video'):
            raise KEEMuImportException

    def _import_taxonomy_preprocessor(self, model_class, data):
        # Currently accepted isn't required so None == Unknown
        try:
            if data['ClaCurrentlyAccepted'] == "Unknown":
                data['ClaCurrentlyAccepted'] = None
        except KeyError:
            pass

        return data

    def _import_catalogue_preprocessor(self, model_class, data):

        # Filter out some of the records

        if not 'ColDepartment' in data:
            log.debug('Skipping record %s: No collection department', data['irn'])
            raise KEEMuImportException

        if not 'AdmDateInserted' in data:
            log.debug('Skipping record %s: No AdmDateInserted', data['irn'])
            raise KEEMuImportException

        # Skip records if SecRecordStatus is one of 'DELETE', 'Reserved', 'Stub', 'Stub Record', 'DELETE-MERGED'
        if 'SecRecordStatus' in data and data['SecRecordStatus'] in ['DELETE', 'Reserved', 'Stub', 'Stub Record', 'DELETE-MERGED']:
            log.debug('Skipping record %s: Incorrect record status', data['irn'])
            raise KEEMuImportException

        # Botany records include ones from Linnean Society. Should be excluded.
        if 'RegHerbariumCurrentOrgAcroLocal' in data and data['RegHerbariumCurrentOrgAcroLocal'] == 'LINN':
            log.debug('Skipping record %s: Non-BM botany record', data['irn'])
            raise KEEMuImportException

        # 4257 Artefacts have no kind or name. Skip them
        # TODO: Test
        if data['ColRecordType'] == 'Artefact' and 'ArtKind' not in data and 'ArtName' not in data:
            raise KEEMuImportException

        # Process determinations
        determinations = data.get('EntIdeTaxonRef', None) or data.get('EntIndIndexLotTaxonNameLocalRef', None)

        if determinations:

            data['specimen_taxonomy'] = []

            determinations = ensure_list(determinations)

            # Load the taxonomy records for these determinations
            taxonomy_records = self.datastore_db_session.query(TaxonomyModel).filter(TaxonomyModel.irn.in_(determinations)).all()

            # Loop through all retrieved taxonomy records, and add a determination for them
            # This will act as a filter, removing all duplicates / missing taxa
            for taxonomy_record in taxonomy_records:
                filed_as = (taxonomy_record.irn == data.get('EntIdeFiledAsTaxonRef', None))
                data['specimen_taxonomy'].append(Determination(taxonomy_irn=taxonomy_record.irn, specimen_irn=data['irn'], filed_as=filed_as))

        # Parasite card host / parasites

        host_parasites = {
            'host': data.get('CardHostRef', []),
            'parasite': data.get('CardParasiteRef', []),
        }

        stages = ensure_list(data.get('CardParasiteStage', []))

        for host_parasite_type, refs in host_parasites.items():
            refs = ensure_list(refs)

            for i, ref in enumerate(refs):
                try:
                    stage = stages[i]
                except IndexError:
                    stage = None

                assoc_object = HostParasiteAssociation(taxonomy_irn=ref, parasite_card_irn=data['irn'], parasite_host=host_parasite_type, stage=stage)

                try:
                    data['host_parasite_taxonomy'].append(assoc_object)
                except KeyError:
                    data['host_parasite_taxonomy'] = [assoc_object]

        # Some special field mappings

        # Try to use PalDetDate is if DarYearIdentified is missing
        if not 'DarYearIdentified' in data:
            try:
                date_matches = re_date.search(data['PalDetDate'])
                if date_matches:
                    data['DarYearIdentified'] = date_matches.group(1)
                    data['DarMonthIdentified'] = date_matches.group(2)
                    data['DarDayIdentified'] = date_matches.group(3)
            except (KeyError, TypeError):
                # If PalDetDate doesn't exists or isn't a string (can also be a list if there's multiple determination dates - which we ignore)
                pass

        # EntCatCatalogueNumber requires EntCatPrefix if it's used in catalogue_number
        try:
            data['EntCatCatalogueNumber'] = '{0}{1}'.format(data['EntCatPrefix'], data['EntCatCatalogueNumber'])
        except KeyError:
            pass

        return data

    def _import_site_preprocessor(self, model_class, data):

        # Initially, we're only going to use single point locations
        # If we have a centroid, use that one
        # If we don't, and we do have multiple points, just use the first one
        for field, centroid_field in [
            ('LatLatitude', 'LatCentroidLatitude'),
            ('LatLatitudeDecimal', 'LatCentroidLatitudeDec'),
            ('LatLongitude', 'LatCentroidLongitude'),
            ('LatLongitudeDecimal', 'LatCentroidLongitudeDec')
        ]:

            centroid_value = data.get(centroid_field, None)

            # If we have a centroid value, use that
            if centroid_value:
                data[field] = centroid_value
            else:
            # Otherwise if it's a list, use the first value
                value = data.get(field, None)

                if isinstance(value, list):
                    data[field] = value[0]


    def _populate_subfield_data(self, fields, data):
        """
        Given a list of fields, group them into a list
        """
        nested_data = []

        for field in fields:
            if field in data:
                # convert to a list if it's not already one
                data[field] = ensure_list(data[field])

                for i, value in enumerate(data[field]):
                    # Convert empty string to None
                    if value == '':
                        value = None
                    try:
                        nested_data[i][field] = value
                    except IndexError:
                        nested_data.append({field: value})

                # Remove the field from the data - do not want to reuse
                del data[field]

        # Dedupe the data
        deduped_nested_data = []

        for i in nested_data:
            if i not in deduped_nested_data:
                deduped_nested_data.append(i)

        return deduped_nested_data

    def _log_status(self, keemu_data):
        # Output status update
        status = keemu_data.get_status()

        if status:
            log.info(status)




