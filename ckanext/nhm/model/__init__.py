from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, PickleType, func
import ckan.model as model

Base = declarative_base()


class Log(Base):

    """
    Table for holding log messages - used for KE EMU DB import errors.
    """

    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    logger = Column(String)
    level = Column(String)
    trace = Column(String)
    msg = Column(String)
    args = Column(PickleType)
    created = Column(DateTime, default=func.now())  # the current timestamp

    def __init__(self, logger=None, level=None, trace=None, msg=None, args=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.trace = trace
        self.msg = msg
        self.args = args

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])


def setup():
    Base.metadata.create_all(model.meta.engine)
