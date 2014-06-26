#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import ckan.model as model
from ckan.model.resource import Resource
from sqlalchemy import MetaData, Column, Integer, String, DateTime, UnicodeText, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DatastoreStats(Base):
    """
    Table for holding resource stats
    """
    __tablename__ = 'datastore_stats'

    id = Column(Integer, primary_key=True)
    resource_id = Column(UnicodeText, ForeignKey(Resource.id))
    date = Column(DateTime, default=func.now())  # the current timestamp
    count = Column(Integer)