# Router imports
import http 

# Scheduler imports
import time, sched
from threading import Thread


class Router():
    def __init__(self, routes):
        super().__init__()
        ''' initialize a Router instance 
            @param: routes -> python dict containing path and handler as key value pair
        '''
        self._routes = routes

    async def __call__(self, ws, path):
        
        await path['handler'](ws, path['path']) 

    def match(self, path):
        """ validate the incoming request path """
        print(f"matching path -> {path}")

        handler = self._routes.get(path, None)
        if handler:
            return {"handler": handler, "path":path, "status":None}
        
        else:
            return {"handler": handler, "path":path, "status":http.HTTPStatus.NOT_FOUND}

class EventManager():
    """ Base class to implement event management
        >>> Must be inherited by a class
        >>> Child class must define a tuple named '__events__' containing name of events  
        >>> eg. __events__  = ('event1', 'event2')
    """

    def __init__(self):
        self._event_callbacks = {event:self._default_callback for event in self.__events__}

    def _default_callback(self, *args):
        """ default callback function for all unregistered events """
        pass

    def bind(self, **kwargs):
        """ bind events with their respective callbacks 
            >>> @params: pass events & their callbacks as named params 
            >>> eg. bind(event1=callback1, event2=callback2) 
        """

        for event, callback in kwargs.items():
            if self._event_callbacks.get(event, None):
                self._event_callbacks[event]    = callback
            
            else:
                print(f"'{event}' is not defined")

    def dispatch(self, event, *args):
        """ dispatch a registered event 
            >>> @param:event    [str]   -> name of registered event  
            >>> @param:args             -> args to pass to the callback
        """

        if self._event_callbacks.get(event, None):
            self._event_callbacks[event](*args)
        else:
            print(f"'{event}' is not defined")

class JobScheduler():
    """ wrapper around sched to schedule jobs """
    _active_jobs = {}
    
    class JobType:
        ONCE    = 0
        REPEAT  = 1

    class Job(Thread):
        """ Module to run a scheduled job """
        
        def __init__(self, target, delay, job_type, data={}):
            super().__init__()
            """ initialize job
                >>> @param:target   -> target function to be executed
                >>> @param:delay    -> waiting time span to start execution of target function [seconds]
                >>> @param:job_type -> JobType.ONCE/JobType.REPEAT
                >>> @param:data     -> python dictionary containing data to passed to target
            """
            self._stop      = False
            self._target    = target
            self._delay     = delay
            self._job_type  = job_type
            self._data      = data
            self._first_run = True
            self._scheduler = sched.scheduler(time.time, time.sleep)

            self.setDaemon(True)
            self.start()
            
        def run(self):
            """ start thread working """
            self._scheduler.enter(1, 1, self._run)
            self._scheduler.run()

        def _run(self):
            """ to run target function """

            if not self._stop:
                if self._first_run:
                    self._first_run = False
                    self._scheduler.enter(self._delay, 1, self._run)
                
                else:    
                    self._target(self._data)
                    if self._job_type == JobScheduler.JobType.REPEAT:
                        self._scheduler.enter(self._delay, 1, self._run)

        def unschedule(self):
            """ cancel scheduled job """
            
            self._stop  = True
            if len(self._scheduler.queue) > 0:
                list(map(self._scheduler.cancel, self._scheduler.queue))        
        
    @classmethod
    def _schedule_job(cls, target, delay, data, job_type):
        """ helper function to schedule a job[do not use this func] """
        
        job_id = id(target)
        if cls._active_jobs.get(job_id, None):
            _job = JobScheduler.Job(target, delay, job_type, data)
            cls._active_jobs[job_id].append(_job)
        
        else:
            _job                    = JobScheduler.Job(target, delay, job_type, data)
            cls._active_jobs[job_id]= [_job]
        
        return _job

    @classmethod
    def schedule(cls, target, delay, data={}):
        """ schedule a job to run after specified time while it is active 
            >>> @param:target   -> target function to be scheduled
            >>> @param:delay    -> waiting time span to start execution of target function [seconds]
            >>> @param:data     -> python dictionary containing data to passed to target
        """

        return cls._schedule_job(target, delay, data, JobScheduler.JobType.REPEAT)

    @classmethod
    def schedule_once(cls, target, delay, data={}):
        """ schedule a job to run after specified time only once 
            >>> @param:target   -> target function to be scheduled
            >>> @param:delay    -> waiting time span to start execution of target function [seconds]
            >>> @param:data     -> python dictionary containing data to passed to target
        """

        return cls._schedule_job(target, delay, data, JobScheduler.JobType.ONCE)

    @classmethod
    def unschedule(cls, target):
        """ unschedule all scheduled jobs for a target function """

        func_id = id(target)
        if cls._active_jobs.get(func_id, None) is not None:
            _   = [j.unschedule() for j in cls._active_jobs[func_id] ]
            
            cls._active_jobs.remove(func_id)
        
    @classmethod
    def unschedule_all(cls):
        """ unschedule all scheduled jobs """

        for key, jobs in cls._active_jobs:
            _   = [job.unschedule() for job in jobs ]
        
        cls._active_jobs.clear()



if __name__ == "__main__":
    # JobScheduler Test
    def test_func(data):
        print(data['request'])

    data = {"request":"This is a request object"}
    JobScheduler.schedule(test_func, 5, data)

    while True:
        inp = input("your input >>> ")
        if inp == "e":
            break
        elif inp == "u":
            JobScheduler.unschedule(test_func)
        
        elif inp == "s":
            _job = JobScheduler.schedule(test_func, 3, data)

        elif inp == "ud":
            _job.unschedule()

        elif inp == "so":
            JobScheduler.schedule_once(test_func, 3, data)


