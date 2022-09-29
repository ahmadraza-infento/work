from utils import Logger
from server import Server
from clientA import Client_A
from clientB import Client_B


def main():
    host = '127.0.0.1'
    port = 12000

    server_socket = Server(host, port)
    server_socket.start()

    client_a = Client_A(host, port)
    client_a.start()

    client_b = Client_B(host, port)
    client_b.start()

    _ = input('press enter to exit driver...')


if __name__ == '__main__':
    main()