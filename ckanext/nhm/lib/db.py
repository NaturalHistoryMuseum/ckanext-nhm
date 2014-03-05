#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import pylons
from sqlalchemy.orm import sessionmaker
from ckanext.datastore.db import _get_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement

def get_datastore_session():
    """
    Get a datastore session to use with SQLA ORM
    """
    # TODO: Change this
    # data_dict = {'connection_url': pylons.config['ckan.datastore.write_url']}
    data_dict = {'connection_url': 'postgresql://ckan_default:asdf@localhost/datastore_default'}
    engine = _get_engine(data_dict)
    session = sessionmaker(bind=engine)
    return session()


class CreateTableAs(Executable, ClauseElement):
    """
    Compiler to use as CREATE TABLE [x] AS [SELECT]
    Used to create the KE EMu datastore table
    """
    def __init__(self, table, select):
        self.table = table
        self.select = select

@compiles(CreateTableAs)
def visit_create_table_as(element, compiler, **kw):
    return "CREATE TABLE \"%s\" AS (%s)" % (
        element.table,
        compiler.process(element.select)
    )
