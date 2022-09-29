import pickle
import socket
from threading import Thread
from utils import Commands, Logger
from multiprocessing import Process


class Server(Process):
    MAX_NUM_CONN = 10  # keeps 10 clients in queue

    def __init__(self, host="127.0.0.1", port=12000):
        super().__init__()

        self.host       = host
        self.port       = port
        self.server     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.handlers   = {} 
        self.key_pairs = {}

    def _bind(self):
        """ bind server with provided host and port
        """
        self.server.bind((self.host, self.port))

    def _listen(self):
        """ listen for client requests
        """
        self.server.listen(self.MAX_NUM_CONN)
        Logger.info(f"Listening at {self.host}/{self.port} ")

    def _accept_clients(self):
        """ accept client requests
        """

        while True:
            client, addr = self.server.accept()
            thread = Thread(target=self._handler, args=(client, addr,))
            thread.setDaemon(True)
            thread.start()
            Logger.info(f'connected with {addr}...')
            self.handlers[addr] = (thread, client)

    def send_response(self, response, clienthandler, addr):
        """ send response to the connected client
        """
        decoded = pickle.dumps(response)
        clienthandler.send(decoded)
        Logger.info(f'server response sent at {addr}')

    def _handler(self, clienthandler, addr):
        """ handler for a connected client, receive & send response to the client     
        """

        while True:
            data    = clienthandler.recv(1024)
            data_str= pickle.loads(data)
            Logger.info(f'received data is: {data_str}')
            
            command = data_str.split(' ')[0]
            if command == Commands.STORE:
                try:
                    data_str            = data_str.replace(Commands.STORE, '').strip()
                    key, value = [ item.strip() for item in data_str.split('=', 2)]
                    self.key_pairs[key] = value
                    
                    Logger.info(f"'{value}' stored for key '{key}'")
                    self.send_response('1', clienthandler, addr)
                except Exception as e:
                    Logger.exception(f'{e}')
                    self.send_response('0', clienthandler, addr)
                
            
            elif command == Commands.GET:
                key = data_str.replace(Commands.GET, '').strip()
                if key in self.key_pairs.keys():
                    response = f"{key} = {self.key_pairs[key]}"

                else:
                    response = f'{Commands.ERROR}'

                self.send_response(response, clienthandler, addr)
            
            else:
                Logger.info(f'invalid request by client {addr}')

    def run(self):
        """ main function for this process
        """
        self._bind()
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    server = Server()
    server.start()
