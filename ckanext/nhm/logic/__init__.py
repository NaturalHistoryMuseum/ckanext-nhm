from ckan.logic import ActionError

class NotDarwinCore(ActionError):
    '''
    Exception raised when resource isn't Darwin Core
    '''
    pass
