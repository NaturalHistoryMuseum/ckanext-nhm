import ckan.plugins as p

get_validator = p.toolkit.get_validator

not_missing = get_validator('not_missing')
resource_id_exists = get_validator('resource_id_exists')
int_validator = get_validator('int_validator')


def nhm_record_get_schema():
    schema = {
        'resource_id': [not_missing, unicode, resource_id_exists],
        'record_id': [not_missing, int_validator]
    }
    return schema