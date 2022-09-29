import os
from datetime import datetime


class Logger():
    """ Module to manage application loges """
    appName     = ''
    logType     = ''
    debugMode   = False
    printlog    = None
    logfolder   = "logs"

    @classmethod
    def init(cls, app_name, logType='s', debug_mode=False):
        ''' manage logging in an application
            @param: app_name    --> name of the application
            @param: logType     s --> standard --> print loges to both terminal and file
                                f --> file     --> print loges to log file only
                                t --> terminal --> print loges to terminal only 
            @param: debug_mode  --> print debug loges as well if set to True
        '''
        cls.appName     = app_name 
        cls.logType     = logType
        cls.debugMode   = debug_mode

        if      logType == 'f':
            cls.printlog   = cls._print_to_file
        
        elif    logType == 't':
            cls.printlog   = cls._print_to_terminal
        
        else:
            cls.printlog   = cls._print_stanard

        if logType in ("s", "f") and not os.path.exists(cls.logfolder):
            os.makedirs(cls.logfolder)

    
    @classmethod
    def _print_to_file(cls, message):
        """ print logs to file 
            >>> @param:message  -> message to be saved
        """
        try:
            ds          = datetime.now().strftime('%Y%m%d%H')
            file_path   = f'{cls.appName}_{ds}.log'
            with open(os.path.join(cls.logfolder, file_path), 'a') as fp:
                fp.write(f'{message}\n')
       
        except Exception as e:
            print('Failed To Open Log File')

    @classmethod        
    def _print_to_terminal(cls, message):
        """ print log to the terminal
            >>> @param:message  -> message to be printed
        """
        print(message)

    @classmethod
    def _print_stanard(cls, message):
        """ print log to the terminal and file
            >>> @param:message  -> message to be displayed as log
        """
        cls._print_to_terminal(message)
        cls._print_to_file(message)

    @classmethod
    def exception(cls, e, occuredAt, id='', debug=False):
        """ display exception message
            >>> @param:e        -> exception message
            >>> @param:occuredAt-> place where exception is raised
            >>> @param:debug    -> mark message as debug
        """
        extras  = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[EXCEPTION]@{occuredAt} --> {e}' if id == '' else f'[EXCEPTION_{id}]@{occuredAt} --> {e}'
        
        if debug:
            if cls.debugMode:
                cls.printlog(message)
        
        else:
            cls.printlog(message)
    
    @classmethod
    def info(cls, message, debug=False):
        """ display info message
            >>> @param:message  -> info message
            >>> @param:debug    -> mark message as debug
        """
        extras  = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[INFO] {message}'
        
        if debug:
            if cls.debugMode:
                cls.printlog(message)
        
        else:
            cls.printlog(message) 

    @classmethod
    def error(cls, message, debug=False):
        """ display error message
            >>> @param:message  -> error message
            >>> @param:debug    -> mark message as debug
        """
        extras  = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]"
        message = f'{extras}[ERROR] {message}'
        
        if debug:
            if cls.debugMode:
                cls.printlog(message)
        
        else:
            cls.printlog(message)

    @classmethod
    def debug(cls, message):
        """ display debug message
            >>> @param:message  -> debug message
        """
        if cls.debugMode:
            cls.printlog(f"[ DEBUG ] {message}")

