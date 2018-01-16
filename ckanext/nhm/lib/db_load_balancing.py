#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import re
import json
import functools
import logging
import urllib2
import psycopg2
import sqlalchemy
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, DisconnectionError
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2


_original_create_engine = None
_last_host = u''
config = {
    u'db_load_balancing.plusmoin_url': u'http://localhost:9815/status.json',
    u'ckan.datastore.read_url': u''
}


def db_load_balancing_init(config_file):
    '''Initialize the database load balancing system.
    
    To circumvent the lack of flexibility in CKAN, this will monkey patch
    SqlAlchemy in order to configure it properly (we do not actually do
    anything that cannot be done via SqlAclhemy configuration). This must
    thus be invoked before ckan is started, eg. in the wsgi file:
    
        from ckanext.nhm.lib.db_load_balancing import db_load_balancing_init
        db_load_balancing_init(config_filepath)
    
    The patching replaces SqlAlchemy's create_engine with our own custom
    version.  See _create_engine for more information on what the patching
    changes and how the load balancing is performed.

    :param config_file: Path to the ckan config file. The following settings
                        are expected in [app:main]:
                        - ckan.datastore.read_url: The read only connection
                        - db_load_balancing.plusmoin_url: URL at which the
                              plusmoin status can be fetched.

    '''
    global _original_create_engine
    global config
    if _original_create_engine is not _create_engine:
        _original_create_engine = sqlalchemy.create_engine
        sqlalchemy.create_engine = _create_engine
        cp = SafeConfigParser(defaults=config)
        cp.read(config_file)
        config = {
            u'db_load_balancing.plusmoin_url': cp.get(u'app:main', u'db_load_balancing.plusmoin_url'),
            u'ckan.datastore.read_url': cp.get(u'app:main', u'ckan.datastore.read_url')
        }


def _create_engine(*args, **kargs):
    '''Replacement for SQLAlchemy's create_engine
    
    Note that this does not do anything we cannot do by configuring SQLAlchemy.
    The only reason for monkey patching is that CKAN does not allow us to
    configure SQLALchemy properly.
    
    This will:
    - Set a custom pool size, timeout, recycle and overflow;
    - Set a custom creator function.
    
    The custom creator function will:
    - Return the connection to the current master for read/write db users;
    - Return connection to any of the slaves known to be working for read
      only db users.
    
    The load balancing is thus done at the connection level - not the statement
    or session level.
    
    We keep pool_recycle resonably low (5mn), so when a server comes back it has
    a chance to join back into the pool reasonably quickly.

    :param *args: 
    :param **kargs: 

    '''
    global _original_create_engine
    global config

    url = args[0]
    conn_info = _parse_conn_info(url)
    dialect = PGDialect_psycopg2(dbapi=psycopg2)
    if url == config[u'ckan.datastore.read_url']:
        creator = functools.partial(
            _read_only_connect,
            dialect,
            conn_info
        )
    else:
        creator = functools.partial(
            _read_write_connect,
            dialect,
            conn_info
        )
    kargs = dict(kargs.items() + {
        u'poolclass': QueuePool,
        u'pool_size': 6,
        u'pool_timeout': 30,
        u'pool_recycle': 300,
        u'max_overflow': 10,
        u'creator': creator
    }.items())

    return _original_create_engine(*args, **kargs)


@event.listens_for(QueuePool, u'checkout')
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    '''Test connections on Pool checkout
    
    This will test the connection on every pool checkout (once per session)
    and raise an exception if the connection is not working.
    
    The Pool will try three times before giving up. If this happens on a
    read only connection, then next time should try a different server -
    maybe with better luck.
    
    If this is a read/write connection and it fails again, then we'll have
    to wait for plusmoin to kick in and promote a new master. Some 500s
    will be seen in the meantime.

    :param dbapi_connection: 
    :param connection_record: 
    :param connection_proxy: 

    '''
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(u'SELECT 1')
    except:
        # The actual exception raised depends on the chosen dialect. We would
        # need to force the dialect (eg. psycopg2) to catch the right
        # exceptions. Given that we log the exception, this catch all should
        # not impact debugging.
        logger = logging.getLogger(u'db_load_balancing')
        logger.exception(u'Database disconnection for %s', dbapi_connection.dsn)
        raise DisconnectionError()
    cursor.close()


def _read_write_connect(dialect, connection_info):
    '''Creator function invoked for creating read/write connections
    
    Note that the parameters are first created using a partial. SqlAlchemy
    invokes this without parameters.
    
    Every time a new connection is created, we query plusmoin for the current
    master and return a connection to that host.

    :param dialect: The SqlAlchemy Dialect class that represents our database
    :param connection_info: dict defining host, port, user, password and database.
    :returns: s: A dbapi object

    '''
    try:
        plusmoin = _plusmoin_status()
        if plusmoin:
            if len(plusmoin[u'clusters']) == 0 or not plusmoin[u'clusters'][0][u'has_master']:
                raise Exception(u'Plusmoin advertises no available masters')
            master = plusmoin[u'clusters'][0][u'master']
        else:
            master = connection_info
        logger = logging.getLogger(u'db_load_balancing')
        logger.debug(u'Read/write connection using %s', str(master))
        return dialect.connect(
            user=connection_info[u'user'],
            password=connection_info[u'password'],
            database=connection_info[u'database'],
            host=master[u'host'],
            port=master[u'port']
        )
except Exception as e:
        import sys
        raise DBAPIError.instance(
            None, None, e, dialect.dbapi.Error,
            connection_invalidated=
                    dialect.is_disconnect(e, None, None)), \
            None, sys.exc_info()[2]


def _read_only_connect(dialect, connection_info):
    '''Creator function invoked for creating read only connections
    
    Note that the parameters are first created using a partial. SqlAlchemy
    invokes this without parameters.
    
    Every time a new connection is created, we query plusmoin for the current
    list of servers, and serve these in a round robin fashion.

    :param dialect: The SqlAlchemy Dialect class that represents our database
    :param connection_info: dict defining host, port, user, password and database.
    :returns: s: A dbapi object

    '''
    global _last_host
    try:
        plusmoin = _plusmoin_status()
        if plusmoin:
            if len(plusmoin[u'clusters']) == 0:
                raise Exception(u'Plusmoin advertises no available servers')
            available = list(plusmoin[u'clusters'][0][u'slaves'])
            if plusmoin[u'clusters'][0][u'has_master']:
                available.append(plusmoin[u'clusters'][0][u'master'])
            if len(available) == 0:
                raise Exception(u'Plusmoin advertises no available servers')
            try:
                p = available.index(_last_host)
                host = available[(p+1) % len(available)]
            except ValueError:
                host = available[0]

            _last_host = host
        else:
            host = connection_info
        logger = logging.getLogger(u'db_load_balancing')
        logger.debug(u'Read only connection using %s', str(host))
        return dialect.connect(
            user=connection_info[u'user'],
            password=connection_info[u'password'],
            database=connection_info[u'database'],
            host=host[u'host'],
            port=host[u'port']
        )
except Exception as e:
        import sys
        raise DBAPIError.instance(
            None, None, e, dialect.dbapi.Error,
            connection_invalidated=
                    dialect.is_disconnect(e, None, None)), \
            None, sys.exc_info()[2]


def _plusmoin_status():
    '''Return the plusmoin status from the configured status url


    :returns: s: dict parsed from the plusmoin status or None on failure.

    '''
    global config
    cx = None
    try:
        cx = urllib2.urlopen(config[u'db_load_balancing.plusmoin_url'])
        return json.loads(cx.read())
except urllib2.URLError:
        logger = logging.getLogger(u'db_load_balancing')
        logger.exception(u'Failed to get plusmoin status')
        return None
    finally:
        if cx:
            cx.close()


def _parse_conn_info(conn_str):
    '''Parse a postgresql connection string

    :param conn_str: Postgresql connection string, of the form
                     postgresql://user:pass@host:port/db
    :returns: s: A dict defining 'user', 'password', 'host',  and 'db'
    :raises s: ValueError if the string cannot be parsed

    '''
    rex = re.compile(r'''^postgresql://
        (?P<user>.+?):
        (?P<password>.+?)@
        (?P<host>.+?)/
        (?P<database>.+)$
    ''', re.X)
    result = rex.match(conn_str)
    if not result:
        raise ValueError()
    return {
        u'user': result.group(u'user'),
        u'password': result.group(u'password'),
        u'host': result.group(u'host'),
        u'database': result.group(u'database')
    }

