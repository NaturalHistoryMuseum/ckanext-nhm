
import logging
from ckan.plugins import toolkit
import ckan.model as model
from ckan.lib.cli import CkanCommand
from ckanext.nhm.model.stats import Base

log = logging.getLogger()

class InitDBCommand(CkanCommand):
    """
    Initialise the local stats database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):

        # Create the tables
        self._load_config()
        Base.metadata.create_all(model.meta.engine)