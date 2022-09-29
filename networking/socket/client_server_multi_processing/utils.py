import os

class Logger:
    """ To Save logs in a file """
    
    @classmethod
    def _write_to_file(cls, message):

        if not os.path.exists('logs'):
            os.mkdir('logs')

        # append log to logfile
        logfile = f"logs.txt" 
        with open(os.path.join('logs', logfile), 'a') as fp:
            fp.write(f'{message}\n')

    @classmethod
    def info(cls, *message):
        message = " ".join(message)
        message = f'[INFO] {message}'
        print(message)
        cls._write_to_file(message)
    
    @classmethod
    def exception(cls, *message):
        message = " ".join(message)
        message = f'[EXCEPTION] {message}'
        print(message)
        cls._write_to_file(message)

    @classmethod
    def error(cls, *message):
        message = " ".join(message)
        message = f'[ERROR] {message}'
        print(message)
        cls._write_to_file(message)
        
        

class Commands:
    STORE   = 'STORE'
    GET     = 'GET'
    ERROR   = 'ERROR'
