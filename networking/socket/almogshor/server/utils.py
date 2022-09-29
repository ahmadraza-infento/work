from email.mime import message
import os
import pickle
from pyexpat.errors import messages
import socket
from loges import Logger
import safeqthreads
from threading import Thread

Logger.init("server_logs")

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
    FIN         = "FIN" # finish working for connected client

    _opcodes    = ("RST", "ACK", "LST", "DL", 
                    "CM", "ACM", "CCN", "MSG", "FIN")
    _client_menu= ("LST", "DL", "CM", "ACM", "CCN", "MSG", "FIN")

    @classmethod
    def validate_opcode(cls, opcode):
        """ return True of opcode is a valid code else False 
            >>> @param:opcode   -> any opcode supported by OpCode
        """
        return True if opcode in cls._opcodes else False

class Handler():
    """ Interface to handle current connected client"""
    _data_folder = "./filesdir"
    
    @classmethod
    def init(cls):
        """ initialize handlers to respond to client requests """
        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.CM       : cls.handle_cm,
                            OpCode.ACM      : cls.handle_acm,
                            OpCode.CCN      : cls.handle_ccn,
                            OpCode.MSG      : cls.handle_msg,
                            OpCode.FIN      : cls.handle_fin
                        }

    @classmethod
    def handle(cls, opcode, client):
        """ base function to handle client's request and pass control to respective handler
            >>> @param:opcode   -> opcode sent by client
            >>> @param:client   -> an instance of ClientInterface class
        """
        
        if OpCode.validate_opcode(opcode) and cls._handlers.get(opcode, None) is not None:
            cls._handlers[opcode](client)

        else:
            Logger.error(f"invalid OpCode [{opcode}] received from [{client._addr}]")
            client._send(OpCode.RST)

    @classmethod
    def handle_msg(cls, client):
        """ send messages related to this client """
        messages = Server.client_messages(client.ClientName)
        messages = f"MSG_{messages}"
        
        client.send(messages)

    @classmethod
    def handle_lst(cls, client):
        """ handle LST request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """ 
        
        resp = '<file_lst>'
        files= os.listdir(cls._data_folder)
        for f in files:
           resp += f'<"{f}">' 
        resp += '<end>'
        client.send(resp)

    @classmethod
    def _send_over_udp(cls, bytes_data, port):
        """ send bytes_data over udp """
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.sendto(bytes_data, ("127.0.0.1", port))
        udp_sock.close()


    @classmethod
    def handle_dl(cls, client):
        """ handle DL request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
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

        client.send(OpCode.SI)
        filename    = client.receive()
        file_path   = os.path.join(cls._data_folder, filename)
        if os.path.exists(file_path):
            bytes_data, length = read_file(file_path)
            if bytes_data:
                client.send(f'{length}')
                resp = client.receive()
                if resp == OpCode.SI:
                    user = client.ClientName
                    cls._send_over_udp(bytes_data, client.Port+1000) 
                    resp = client.receive()
                    if resp == OpCode.ACK:
                        Logger.info(f"requested file [{filename}] sent to [{user}]")
                    
                    else:
                        Logger.error(f"client [{user}] failed to receive file [{filename}]")

                else:
                    Logger.info(f"client not ready to receive file [{filename}]")
            
            else:
                Logger.error(f'failed to read file [{filename}]')
                client.send(OpCode.RST)
        
        else:
            Logger.error("file not found")
            client.send(OpCode.RST)

    @classmethod
    def handle_cm(cls, client):
        """ handle CM request from client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        client.send     (OpCode.SI)
        target_client   = client.receive()
        client.send     (OpCode.SI)
        msgs            = client.receive() 
        if Server.send(target_client, msgs):
            client.send (OpCode.ACK)
        
        else:
            client.send(OpCode.RST)

    @classmethod
    def handle_acm(cls, client):
        """ handle ACM request by the user 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        client.send     (OpCode.SI)
        msgs            = client.receive() 
        if Server.send_to_all(client.ClientName, msgs):
            client.send (OpCode.ACK)
        
        else:
            client.send(OpCode.RST)
        
    @classmethod
    def handle_ccn(cls, client):
        """ handle CCN request by client
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        clients     = Server.connected_clients()
        clients.remove(client.ClientName)
        clients_str = f'<users_lst><{len(clients)}>'
        for cl in clients:
            clients_str += f'<"{cl}">'
        clients_str += '<end>'
        client.send(clients_str)
        
    @classmethod
    def handle_fin(cls, client):
        """ handle finish request by the client
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        Logger.info(f'ending session with {client._addr}')
        client.send(OpCode.ACK)
        client.stop()

class ClientInterface(Thread):
    """ module to handle client connected with server """

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

    def send(self, data, sendall=False, serialize=True):
        """ send data to the connected client
            >>> @param:data     -> data to be sent to the client
            >>> @param:sendall  -> flag to send all data in one go
            >>> @param:serialize-> flag to serialize data before sending to client
        """

        serialized_data = pickle.dumps(data) if serialize else data
        if sendall:
            self._client.sendall(serialized_data)   

        else: 
            self._client.send(serialized_data)

    def receive(self, bytes_len=4090, deserialize=True):
        """ receive message from connected client
            >>> @param:bytes_len    -> length of bytes to be received from client
            >>> @param:deserialize  -> flag to deserialize data received from client
        """
        data    = self._client.recv(bytes_len)
        data_str= pickle.loads(data) if deserialize else data
        return data_str

    def stop(self):
        """ stop loop for connected client """

        self._STOP = True

    def run(self):
        """ entry point for client interface to maintain a loop while client is 
            connected with server 
        """

        Logger.info(f"session with {self._addr} started")
        try:
            while self._STOP is False:
                request = self.receive()
                Handler.handle(request, self)
        
        except Exception as e:
            Logger.exception(e, f'run[{self._addr}]')
        
        finally:
            Server.on_client_disconnected(self._name, self._addr)
            Logger.info(f"session with client [{self._addr}] ended")
            
class Server(safeqthreads.SafeWorker):
    """ Core module for server """

    MAX_NUM_CONN= 10  # keeps 10 clients in queue
    _self       = None

    @classmethod
    def init(cls, thread, signal, host, port, port_range, ui):
        cls._self = Server(thread, signal, host, port, port_range, ui)
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
            Logger.info(f"message [{message}] scheduled for [{name}]")
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
        Logger.info(f"available ports -> {self._available_ports}")
        self._client_handlers.pop(name, None)
        self.ui_signal.info.emit(f"{len(self.connected_clients())}_{len(self._available_ports)}")
        self.send_to_all(name, f"<user '{name}' has disconnected>")
    #endregion


    def __init__(self, thread, signal, host, port, port_range, ui):
        """ initialize server using socket module
            >>> @param:host         -> ip address for server
            >>> @param:port         -> port to open by server to receive client request
            >>> @param:port_range   -> range of ports, server should work
            >>> @param:ui           -> ui instance to set server logs
        """
        
        super(Server, self).__init__(thread)
        self.host               = host
        self.port               = port
        self.port_range         = port_range
        self.server             = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self._client_handlers   = {} 
        self._available_ports   = [p for p in port_range]
        self._ui                = ui
        self.ui_thread          = thread
        self.ui_signal          = signal
        self._message_queue     = {}

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
        Logger.info(f"Listening at {self.host}/{self.port} ")
        self.ui_signal.logger.emit(f"Listening at {self.host}/{self.port} ")

    def _username(self, client):
        """ receive and validate username from client"""

        name = pickle.loads( client.recv(512) )
        if name in self._client_handlers.keys():
            client.send(pickle.dumps(OpCode.RST))
            return None
        
        else:
            client.send(pickle.dumps(OpCode.ACK))
            return name

    def _verify_port(self, port):
        """ verify that if port is available or not
            >>> @return: True if port is available, False otherwise
        """
        return True if port in self._available_ports else False

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
        self.ui_signal.info.emit(f"{len(self.connected_clients())}_{len(self._available_ports)}")
        self._push_message(name, "<you have been connected!>")
        self.send_to_all(name, f"<user '{name}' has connected>")

    def _accept_clients(self):
        """ accept client request and start ClientInterface for individual client """

        while True:
            client, addr= self.server.accept()
            Logger.info(f"connection request received from {addr}")
            self.ui_signal.logger.emit(f"connection request received from {addr}")
            if self._verify_port(addr[1]):
                client.send( pickle.dumps(OpCode.ACK) )
                name = self._username(client)
                if name:
                    self._init_client_interface(client, addr, name)
                else:
                    Logger.info(f"Connection Refused[{addr}]: username already registered")
                    self.ui_signal.logger.emit(f"Connection Refused[{addr}]: username already registered")
            else:
                Logger.error(f'Connection Refused[{addr}]: port [{addr[1]}] already in use')
                self.ui_signal.logger.emit(f'Connection Refused[{addr}]: port [{addr[1]}] already in use')
                client.send(pickle.dumps(OpCode.RST))
    
    def run(self):
        """ entr point for server module """
        self._bind()
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    Handler.init()
    Server.init(host="127.0.0.1", port=50000, port_range=range(50001, 50016))
