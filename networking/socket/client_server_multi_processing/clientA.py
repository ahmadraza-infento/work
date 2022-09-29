import socket
import pickle
import argparse
from utils import Commands, Logger
from multiprocessing import Process


class Client_A(Process):

    def __init__(self, server_ip=None, port=None):
        """
        Class constructor
        """
        super().__init__()
        self.client     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_ip = server_ip
        self._port      = port

    def connect(self, ip_addr='127.0.0.1', port=12000):
        """connect with server on provided address & port
        """
        self.client.connect((ip_addr, port))

    def send(self, data):
        """ send request to the server, connected with
        """
        serialized_data = pickle.dumps(data)
        self.client.send(serialized_data)

    def store_key(self, key, value):
        """ store a key and value pair on server, connected with
        """
        request = f'{Commands.STORE} {key} = {value}'
        self.send(request)
        Logger.info(f'[Client_A] {request} sent to server')
        
        response = self.receive()
        if response == '1':
            Logger.info(f'[Client_A] {request} succeeded')
        else:
            Logger.info(f'[Client_A] {request} failed')

    def receive(self, max_alloc_buffer=4090):
        """ receive message from server, connected with
        """
        data    = self.client.recv(max_alloc_buffer)
        data_str= pickle.loads(data)
        return data_str

    def _send_test(self, request):
        """ send test request to the server, connected with
        """
        self.send(request)
        Logger.info(f'[Client_A] {request} sent to server')
        
        response = self.receive()
        if response == '1':
            Logger.info(f'[Client_A] {request} succeeded')
        else:
            Logger.info(f'[Client_A] {request} failed')

    def run(self):
        """entry point for this class
        """
        self.connect(self._server_ip, self._port)
        Logger.info('[Client_A] connection established with server successfully...')

        ''' test requests '''
        self._send_test(f'{Commands.STORE} ping = Jon Doe')
        self._send_test(f'{Commands.STORE} job = multiprocessing')
        self._send_test(f'{Commands.STORE} music = Love music')
        self._send_test(f'{Commands.STORE} language = python')
        self._send_test(f'{Commands.STORE} lib = socket')
        self._send_test(f'{Commands.STORE} username = Alice')
        

    def close(self):
        """ close active client
        """
        self.client.close()


# main code to run client
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--key',  default=None)
    parser.add_argument('--value',default=None)
    args = parser.parse_args()

    server_ip = '127.0.0.1'  # this is the servers ip address
    server_port = 12000
    client = Client_A()
    client.connect(server_ip, server_port)  # creates a connection with the server
    
    if args.key is not None and args.value is not None:
        request = f'{Commands.STORE} {args.key} = {args.value}'

    else:
        key     = input('enter key name >>>')
        value   = input(f"value for '{key}' >>>")
        request = f'{Commands.STORE} {key} = {value}'
    
    client.send(request)
    Logger.info(f'[Client_A] {request} sent to server')

    y = input('press enter to exit...')
