#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import functools
import json
import logging
import re

import psycopg2
import sqlalchemy
import urllib2
from ConfigParser import SafeConfigParser
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.exc import DBAPIError, DisconnectionError
from sqlalchemy.pool import QueuePool

_original_create_engine = None
_last_host = ''
config = {
    'db_load_balancing.plusmoin_url': 'http://localhost:9815/status.json',
    'ckan.datastore.read_url': ''
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
            'db_load_balancing.plusmoin_url': cp.get('app:main', 'db_load_balancing.plusmoin_url'),
            'ckan.datastore.read_url': cp.get('app:main', 'ckan.datastore.read_url')
        }


def _create_engine(*args, **kargs):
    '''Replacement for SQLAlchemy's create_engine

    Note that this does not do anything we cannot do by configuring SQLAlchemy.
    The only reason for monkey patching is that CKAN does not allow us to
    configure SQLALchemy properly.
    # TODO: check if this is still the case

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
    if url == config['ckan.datastore.read_url']:
        creator = functools.partial(_read_only_connect, dialect, conn_info)
    else:
        creator = functools.partial(_read_write_connect, dialect, conn_info)
    kargs = dict(kargs.items() + {
        'poolclass': QueuePool,
        'pool_size': 6,
        'pool_timeout': 30,
        'pool_recycle': 300,
        'max_overflow': 10,
        'creator': creator
    }.items())

    return _original_create_engine(*args, **kargs)


@event.listens_for(QueuePool, 'checkout')
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
        cursor.execute('SELECT 1')
    except:
        # The actual exception raised depends on the chosen dialect. We would
        # need to force the dialect (eg. psycopg2) to catch the right
        # exceptions. Given that we log the exception, this catch all should
        # not impact debugging.
        logger = logging.getLogger('db_load_balancing')
        logger.exception('Database disconnection for %s', dbapi_connection.dsn)
        raise DisconnectionError()
    cursor.close()


def _read_write_connect(dialect, connection_info):
    '''Creator function invoked for creating read/write connections

    Note that the parameters are first created using a partial. SqlAlchemy
    invokes this without parameters.

    Every time a new connection is created, we query plusmoin for the current
    master and return a connection to that host.

    :param dialect: the SqlAlchemy Dialect class that represents our database
    :param connection_info: dict defining host, port, user, password and database

    :returns: a dbapi object

    '''
    try:
        plusmoin = _plusmoin_status()
        if plusmoin:
            if len(plusmoin['clusters']) == 0 or not plusmoin['clusters'][0][
                'has_master']:
                raise Exception('Plusmoin advertises no available masters')
            master = plusmoin['clusters'][0]['master']
        else:
            master = connection_info
        logger = logging.getLogger('db_load_balancing')
        logger.debug('Read/write connection using %s', str(master))
        return dialect.connect(user=connection_info['user'],
                               password=connection_info['password'],
                               database=connection_info['database'],
                               host=master['host'], port=master['port'])
    except Exception as e:
        import sys
        raise DBAPIError.instance(None, None, e, dialect.dbapi.Error,
                                  connection_invalidated=dialect.is_disconnect(e, None, None))(
            None).with_traceback(sys.exc_info()[2])


def _read_only_connect(dialect, connection_info):
    '''Creator function invoked for creating read only connections

    Note that the parameters are first created using a partial. SqlAlchemy
    invokes this without parameters.

    Every time a new connection is created, we query plusmoin for the current
    list of servers, and serve these in a round robin fashion.

    :param dialect: the SqlAlchemy Dialect class that represents our database
    :param connection_info: dict defining host, port, user, password and database

    :returns: a dbapi object

    '''
    global _last_host
    try:
        plusmoin = _plusmoin_status()
        if plusmoin:
            if len(plusmoin['clusters']) == 0:
                raise Exception('Plusmoin advertises no available servers')
            available = list(plusmoin['clusters'][0]['slaves'])
            if plusmoin['clusters'][0]['has_master']:
                available.append(plusmoin['clusters'][0]['master'])
            if len(available) == 0:
                raise Exception('Plusmoin advertises no available servers')
            try:
                p = available.index(_last_host)
                host = available[(p + 1) % len(available)]
            except ValueError:
                host = available[0]

            _last_host = host
        else:
            host = connection_info
        logger = logging.getLogger('db_load_balancing')
        logger.debug('Read only connection using %s', str(host))
        return dialect.connect(user=connection_info['user'],
                               password=connection_info['password'],
                               database=connection_info['database'], host=host['host'],
                               port=host['port'])

    except Exception as e:
        import sys
        raise DBAPIError.instance(None, None, e, dialect.dbapi.Error,
                                  connection_invalidated=dialect.is_disconnect(e, None,
                                                                               None))(
            None).with_traceback(sys.exc_info()[2])


def _plusmoin_status():
    '''Return the plusmoin status from the configured status url.

    :returns: dict parsed from the plusmoin status or None on failure.

    '''
    global config
    cx = None
    try:
        cx = urllib2.urlopen(config['db_load_balancing.plusmoin_url'])
        return json.loads(cx.read())
    except urllib2.URLError:
        logger = logging.getLogger('db_load_balancing')
        logger.exception('Failed to get plusmoin status')
        return None
    finally:
        if cx:
            cx.close()


def _parse_conn_info(conn_str):
    '''Parse a postgresql connection string

    :param conn_str: postgresql connection string, of the form
                     postgresql://user:pass@host:port/db

    :returns: a dict defining 'user', 'password', 'host',  and 'db'
    :raises ValueError: if the string cannot be parsed

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
        'user': result.group('user'),
        'password': result.group('password'),
        'host': result.group('host'),
        'database': result.group('database')
    }
