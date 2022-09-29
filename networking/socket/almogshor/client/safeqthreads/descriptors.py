'''
we'll create a stop_running attribute for our threads that must be a bool
'''
from weakref import WeakKeyDictionary
from . import errors


class StopRunning(object):
    ''' A descriptor that requires a bool value for the stopRunning attribute '''
    def __init__(self, default=False):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        ''' get the attribute stop_running for this object
            default is False
        '''
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        ''' set the value for stop_running
            an error is raised if this is not a boolean type
        '''
        if not isinstance(value, bool):
            raise errors.StopRunningNotBoolError
        self.data[instance] = value
