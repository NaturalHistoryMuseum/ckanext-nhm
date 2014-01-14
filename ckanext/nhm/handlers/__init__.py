#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'Ben Scott' on 2013-06-21.
"""

import logging
import traceback
import ckan.model as model
from ckanext.nhm.model import Log


class SQLAlchemyHandler(logging.Handler):
    # A very basic logger that commits a LogRecord to the SQL Db
    def emit(self, record):

        trace = None
        exc = record.__dict__['exc_info']

        if exc:
            trace = traceback.format_exc(exc)
        log = Log(
            logger=record.__dict__['name'],
            level=record.__dict__['levelname'],
            trace=trace,
            msg=record.__dict__['msg'],
            args=record.args
        )

        model.Session.add(log)
        model.Session.commit()