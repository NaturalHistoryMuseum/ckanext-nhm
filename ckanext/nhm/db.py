import sqlalchemy
from sqlalchemy.orm import sessionmaker

_engines = {}
                            
def _get_engine(data_dict):
    '''Get either read or write engine.'''
    connection_url = data_dict['connection_url']
    engine = _engines.get(connection_url)

    if not engine:
        engine = sqlalchemy.create_engine(connection_url)
        _engines[connection_url] = engine
    return engine

def _make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


