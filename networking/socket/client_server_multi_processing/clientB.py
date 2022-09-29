import socket
import pickle
import argparse
from utils import Commands, Logger
from multiprocessing import Process


class Client_B(Process):

    def __init__(self, server_ip=None, port=None):
        """Class constructor
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

    def get_key(self, key):
        """ get value for a key from server, connected with
        """
        request = f'{Commands.GET} {key}'
        self.send(request)
        response = self.receive()
        return response

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
        response = self.receive()
        Logger.info(f'[Client_B] server response on [{request}] is -> {response}')

    def run(self):
        """entry point for this class
        """
        self.connect(self._server_ip, self._port)
        Logger.info('[Client_B] connection established with server successfully...')

        ''' test requests '''
        self._send_test(f'{Commands.GET} username')
        self._send_test(f'{Commands.GET} ping')
        self._send_test(f'{Commands.GET} job')
        self._send_test(f'{Commands.GET} music')
        self._send_test(f'{Commands.GET} language')
        self._send_test(f'{Commands.GET} lib')
        self._send_test(f'{Commands.GET} username')

    def close(self):
        """ close active client
        """
        self.client.close()


# main code to run client
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--key',  default=None)
    args = parser.parse_args()

    server_ip = '127.0.0.1'  # this is the servers ip address
    server_port = 12000
    client = Client_B()
    client.connect(server_ip, server_port)  # creates a connection with the server
    
    if args.key is not None:
        request = f'{Commands.GET} {args.key}'

    else:
        key= input('key to get >>>')
        request = f'{Commands.GET} {key}'
    
    client.send(request)
    response = client.receive()
    Logger.info(f'server response on [{request}] is -> {response}')
    y = input('press enter to exit...')
