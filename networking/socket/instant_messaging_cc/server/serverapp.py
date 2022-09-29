from operator import length_hint
import os
import pickle
import socket
from random import randint
from threading import Thread


class OpCode:
    """ Base module to represent operations codes """
    # codes for internel server working
    RST         = "RST" # server will respond with RST, if wrong packet is received
    ACK         = "ACK" # acknowledgement 
    SI          = "SI"  # send info, response if server needs more info
    
    # operations suported for client
    LST         = "LST" # list files
    DL          = "DL"  # download file
    CM          = "CM"  # single client message
    ACM         = "ACM" # message for all clients
    CCN         = "CCN" # connected client names
    MSG         = "MSG" # message

class Handler():
    """ Interface to handle current connected client"""
    _data_folder= "./filesdir"
    _UDP_SIZE   = 512
    _UDP_TIMEOUT= 3.0
    
    @classmethod
    def init(cls):
        """ initialize handlers to respond to client requests """
        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.CM       : cls.handle_cm,
                            OpCode.ACM      : cls.handle_acm,
                            OpCode.CCN      : cls.handle_ccn,
                            OpCode.MSG      : cls.handle_msg
                        }

    @classmethod
    def handle(cls, opcode, ci):
        """ base function to handle client's request and pass control to respective handler
            >>> @param:opcode   -> opcode sent by client
            >>> @param:client   -> an instance of ClientInterface class
        """
        
        cls._handlers[opcode](ci)

    @classmethod
    def handle_msg(cls, ci):
        """ send messages related to this ci """
        messages = Server.client_messages(ci.ClientName)
        messages = f"MSG_{messages}"
        
        ci.send(messages)

    @classmethod
    def handle_lst(cls, ci):
        """ handle LST request by ci 
            >>> @param:ci   -> ClientInterface instance, represents to current 
                                    connected client
        """ 
        
        resp = '<file_lst>'
        files= os.listdir(cls._data_folder)
        for f in files:
           resp += f'<"{f}">' 
        resp += '<end>'
        ci.send(resp)

    @classmethod
    def _udp_packet(cls, id, content):
        packet = {'seqnum':id, 'content':content}
        packet = pickle.dumps(packet)
        return packet

    @classmethod
    def _send_over_udp(cls, bytes_data, addr): 
        """ send bytes_data over udp """
        def send_packet(udpsock, address, datatosend, seqnum):
            resend_timeouts = [0.5, 1.5, 2.5]
            flag = True
            while flag:
                packet = cls._udp_packet(seqnum, datatosend)
                udpsock.sendto(packet, address)
                
                try:
                    udpsock.settimeout(resend_timeouts.pop())
                    ack, _  = udpsock.recvfrom(cls._UDP_SIZE) 
                    
                    if int(pickle.loads(ack)) == seqnum: 
                        flag = False
                except Exception as e:
                    if len(resend_timeouts) == 0:
                        return False
                    
                    else:
                        print(f"Timed Out: Acknowledgement not received for '{seqnum}' ")
                        print(f"resending packet '{seqnum}'")
            return True
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        seqnumber   = randint(0, 4096)
        stop        = False
        while stop is False:
            if len(bytes_data)+4 > cls._UDP_SIZE:
                data = bytes_data[:cls._UDP_SIZE]
                stop = not send_packet(udp_sock, addr, data, seqnumber)
                bytes_data= bytes_data[cls._UDP_SIZE:]
            
            else:
                bytes_data += b"yyyy"
                send_packet(udp_sock, addr, bytes_data, seqnumber)
                stop = True
            seqnumber += 1

        udp_sock.close()


    @classmethod
    def handle_dl(cls, ci):
        """ handle DL request by client 
            >>> @param:ci   -> ClientInterface instance, represents to current 
                                    connected client
        """
        def read_file(fpath):
            """ read file content from active client's directory 
                >>> @param:fpath    -> file path
            """
            if os.path.exists(fpath):
                with open(fpath, 'rb') as f:
                    bytes_data = f.read()
                
                return bytes_data, len(bytes_data)

            else:
                return (None, 0)

        ci.send(OpCode.SI)
        filename    = ci.receive()
        file_path   = os.path.join(cls._data_folder, filename)
        if os.path.exists(file_path):
            bytes_data, length = read_file(file_path)
            if bytes_data:
                ci.send(f'{length}')
                resp = ci.receive()
                if resp == OpCode.SI:
                    user    = ci.ClientName
                    udpaddr = ci.receive()
                    cls._send_over_udp(bytes_data, udpaddr)  
                    resp = ci.receive()
                    if resp == OpCode.ACK:
                        print(f"requested file [{filename}] sent to [{user}]")
                    
                    else:
                        print(f"client [{user}] failed to receive file [{filename}]")

                else:
                    print(f"client not ready to receive file [{filename}]")
            
            else:
                ci.send(OpCode.RST)
        
        else:
            ci.send(OpCode.RST)

    @classmethod
    def handle_cm(cls, ci):
        """ handle CM request from client 
            >>> @param:ci   -> ClientInterface instance, represents to current 
                                    connected client
        """
        ci.send     (OpCode.SI)
        target_client   = ci.receive()
        ci.send     (OpCode.SI)
        msgs            = ci.receive() 
        if Server.send(target_client, msgs):
            ci.send (OpCode.ACK)
        
        else:
            ci.send(OpCode.RST)

    @classmethod
    def handle_acm(cls, ci):
        """ handle ACM request by the user 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        ci.send     (OpCode.SI)
        msgs            = ci.receive() 
        if Server.send_to_all(ci.ClientName, msgs):
            ci.send (OpCode.ACK)
        
        else:
            ci.send(OpCode.RST)
        
    @classmethod
    def handle_ccn(cls, ci):
        """ handle CCN request by client
            >>> @param:ci   -> ClientInterface instance, represents to current 
                                    connected client
        """
        clients     = Server.connected_clients()
        clients.remove(ci.ClientName)
        clients_str = f'<users_lst><{len(clients)}>'
        for cl in clients:
            clients_str += f'<"{cl}">'
        clients_str += '<end>'
        ci.send(clients_str)
        
class ClientInterface(Thread):
    """ Module to handle communication of client connected with server """

    def __init__(self, client, addr, name="", **kwargs) -> None:
        """ initialize client interface for client connected with server 
            >>> @param:client   -> socket instance for connected client
            >>> @param:addr     -> address of connected client
            >>> @param:name     -> name of connected client
        """
        super().__init__(**kwargs)
        
        self._client    = client
        self._addr      = addr
        self._name      = name
        self._STOP      = False
        self._USER      = None

    @property
    def Port(self):
        return self._addr[1]

    @property
    def ClientName(self):
        """ return name of connected client"""
        return self._name

    def send(self, data):
        """ send data to the connected client
            >>> @param:data     -> data to be sent to the client
        """
        self._client.send(pickle.dumps(data))

    def receive(self, bytes_len=4090):
        """ receive message from connected client
            >>> @param:bytes_len    -> length of bytes to be received from client
        """
        return   pickle.loads(self._client.recv(bytes_len)) 

    def stop(self):
        """ stop loop for connected client """

        self._STOP = True

    def run(self):
        try:
            while self._STOP is False:
                request = self.receive()
                Handler.handle(request, self)
        
        except Exception as e:
            print(f'clinet [{self._addr}] disconnnected')
        
        finally:
            Server.on_client_disconnected(self._name, self._addr)
            
class Server():
    """ Core module for server """

    MAX_NUM_CONN= 10  # keeps 10 clients in queue
    _self       = None

    @classmethod
    def init(cls, host, port, port_range):
        cls._self = Server(host, port, port_range)
        return cls._self

    #region Helpers
    @classmethod
    def client_messages(cls, name):
        """ send scheduled messages for client 
            >>> @param:name -> name of the client
        """
        messages = cls._self._message_queue.pop(name, [])
        return " ".join(messages) if len(messages) > 0 else ""

    @classmethod
    def connected_clients(cls):
        """ return name of all connected clients as list """
        return list( cls._self._client_handlers.keys() )
    
    @classmethod
    def send(cls, name, message):
        """ send message to a connected client 
            >>> @param:name     -> name of connected client
            >>> @param:message  -> message to be sent to client
            >>> @return         -> True if message sent, otherwise False
        """
        self    = cls._self
        if name in self._client_handlers.keys():
            cls._self._push_message(name, message)
            return True
        
        else:
            return False
    
    @classmethod
    def send_to_all(cls, name, message):
        """ send message to all connected client
            >>> @param:name     -> name of the calling client 
            >>> @param:message  -> message to be sent to clients
            >>> @return         -> True if message sent, otherwise False
        """
        self    = cls._self
        for client_name in self._client_handlers.keys():
            if client_name != name:
                cls._self._push_message(client_name, message)
        
        return True
    
    @classmethod
    def on_client_disconnected(cls, name, addr):
        """ callback to be called when a client is disconnected
            >>> @param:name -> name of client
            >>> @param:addr -> address of client
        """
        self = cls._self
        self._available_ports.append(addr[1])
        self._client_handlers.pop(name, None)
        self.send_to_all(name, f"<user '{name}' has disconnected>")
    #endregion


    def __init__(self, host, port, port_range):
        """ initialize server using socket module
            >>> @param:host         -> ip address for server
            >>> @param:port         -> port to open by server to receive client request
            >>> @param:port_range   -> range of ports, server should work
        """
        super().__init__()
        self.host               = host
        self.port               = port
        self.port_range         = port_range
        self.server             = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self._client_handlers   = {} 
        self._available_ports   = [p for p in port_range]
        self._message_queue     = {}
        self._thread            = Thread(target=self.run)
        self._thread.setDaemon(True)
        self._thread.start()

    def _push_message(self, client_name, message):
        """ push client message in queue to send """
        if self._message_queue.get(client_name, None):
            self._message_queue[client_name].append(message)
        
        else:
            self._message_queue[client_name] = [message]

    def _bind(self):
        """ bind server with provided host and port"""
        self.server.bind((self.host, self.port))

    def _listen(self):
        """ start listening for client requests """
        self.server.listen(self.MAX_NUM_CONN)
        print(f"Listening at {self.host}/{self.port} ")

    def _verify_port(self, port):
        """ verify that if port is available or not
            >>> @return: True if port is available, False otherwise
        """
        return True if port in self._available_ports else False

    def _username(self, client):
        """ receive and validate username from client"""

        name = pickle.loads( client.recv(512) )
        if name in self._client_handlers.keys():
            client.send(pickle.dumps(OpCode.RST))
            return None
        
        else:
            client.send(pickle.dumps(OpCode.ACK))
            return name

    def _init_client_interface(self, client, addr, name):
        """ initialize interface to handle client requests 
            >>> @param:client   -> socket instance for client
            >>> @param:addr     -> address of connected client
            >>> @param:name     -> name of connected client
        """

        thread = ClientInterface(client, addr, name)
        thread.setDaemon(True)
        thread.start()
        self._client_handlers[name] = (thread, client)
        self._available_ports.remove(addr[1])
        self._push_message(name, "<you have been connected!>")
        self.send_to_all(name, f"<user '{name}' has connected>")

    def _accept_clients(self):
        """ accept client request and start ClientInterface for individual client """

        while True:
            client, addr= self.server.accept()
            print(f"connection request received from {addr}")
            
            if self._verify_port(addr[1]):
                client.send( pickle.dumps(OpCode.ACK) )
                name = self._username(client)
                if name:
                    self._init_client_interface(client, addr, name)
                else:
                    print(f"Connection Refused[{addr}]: username already registered")
            else:
                print(f'Connection Refused[{addr}]: port [{addr[1]}] already in use')
                client.send(pickle.dumps(OpCode.RST))
    
    def run(self):
        """ entr point for server module """
        self._bind()
        self._listen()
        self._accept_clients()



if __name__ == '__main__':
    Handler.init()
    Server.init(host="127.0.0.1", port=50000, port_range=range(50001, 50016))

    _ = input("press enter to exit")
