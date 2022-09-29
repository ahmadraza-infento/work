'''
here we define errors for this package
'''

class SafeQThreadsError(Exception):
    ''' Base-class for all exceptions raised by this module '''


class StopRunningNotBoolError(SafeQThreadsError):
    ''' stop_running must be a boolean value '''
    def __init__(self):
        super(StopRunningNotBoolError, self).__init__("stop_running must be a boolean value!")


class WorkerTypeError(SafeQThreadsError):
    ''' any workers registered must be of the type SafeWorker '''
    def __init__(self):
        super(WorkerTypeError, self).__init__("worker must be an instance of SafeWorker!")


class WorkerAlreadyRegisteredError(SafeQThreadsError):
    ''' raise where we have already registered a SafeWorker instance for this thread '''
    def __init__(self):
        super(WorkerAlreadyRegisteredError, self).__init__("A worker has already been registered for this thread!")


class SafeQThreadTypeError(SafeQThreadsError):
    ''' raise where the object provided is not an instance of SafeQThread '''
    def __init__(self):
        super(SafeQThreadTypeError, self).__init__("The thread object provided must be an instance of SafeQThread!")


class MaxWaitSecondsTypeError(SafeQThreadsError):
    ''' raise where '''
    def __init__(self):
        super(MaxWaitSecondsTypeError, self).__init__("max_wait_seconds must be of the type int!")
