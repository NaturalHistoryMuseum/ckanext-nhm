#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import pylons
from sqlalchemy.orm import sessionmaker
from ckanext.datastore.db import _get_engine
from sqlalchemy.ext import compiler
from sqlalchemy.sql.expression import Executable, ClauseElement

def get_datastore_session():
    """
    Get a datastore session to use with SQLA ORM
    """
    data_dict = {'connection_url': pylons.config['ckan.datastore.write_url']}
    engine = _get_engine(data_dict)
    session = sessionmaker(bind=engine)
    return session()


class InsertFromSelect(Executable, ClauseElement):
    """
    Compiler to use as INSERT INTO t1 (SELECT * FROM t2)
    table.insert().from_select(select) is not available in sqla 0.7.8
    """
    def __init__(self, table, select):
        self.table = table
        self.select = select

@compiler.compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    return "INSERT INTO %s (%s)" % (
        compiler.process(element.table, asfrom=True),
        compiler.process(element.select)
    )

class CreateAsSelect(Executable, ClauseElement):
    """
    Compiler to use as CREATE VIEW|TABLE [x] AS [SELECT]
    """
    def __init__(self, name, select, object_type="TABLE"):
        self.name = name
        self.select = select
        self.object_type = object_type

@compiler.compiles(CreateAsSelect)
def visit_create_as_select(element, compiler, **kw):
    return "CREATE %s \"%s\" AS (%s)" % (
        element.object_type,
        element.name,
        compiler.process(element.select)
    )