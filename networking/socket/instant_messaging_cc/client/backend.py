import socket
import pickle


class OpCode:
    """ Base module to represent operations codes"""
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
    """ interface to handle client input"""
    _UDP_SIZE   = 557

    @classmethod
    def init(cls):
        """ initialize the handlers for client operations """

        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.CM       : cls.handle_cm,
                            OpCode.ACM      : cls.handle_acm,
                            OpCode.CCN      : cls.handle_ccn
                        }

    @classmethod
    def handle(cls, opcode, client, args={}):
        """ handle client input and pass the control to respective handler 
            >>> @param:opcode   -> operation code selected by client
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        return cls._handlers[opcode](client, args)

    @classmethod
    def request_messages(cls, client):
        client.send(OpCode.MSG)
        client.receive(msg=True)
    
    @classmethod
    def handle_lst(cls, client, args):
        """ handle LST operation, to list files at server 
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> user input required to handle operation 
        """
        
        client.send(OpCode.LST)
        resp = client.receive()
        return resp

    @classmethod
    def _init_udp_client(cls):
        from random import randint
        while True:
            try:
                port = randint(1024, 49152)
                udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_client.bind(('127.0.0.1', port))
                return udp_client, ('127.0.0.1', port)
            except:
                pass

    @classmethod
    def _receive_over_udp(cls, length, udp_client, set_pb): 
        """ receive udp packet over given port 
            @param:length   -> length of bytes to be received
            @param:addr     -> addr to receive data over
            @param:set_pb   -> func reference to set downloading progress over GUI
        """

        bytes_data = b""
        received_bytes = {}
        while True:
            packet, saddr = udp_client.recvfrom(cls._UDP_SIZE)
            if len(packet) == 0 :
                break

            else:
                packet  = pickle.loads(packet)
                seqnum  = packet.get("seqnum") 
                content = packet.get("content") 
                udp_client.sendto(pickle.dumps(seqnum), saddr)

                if content[-4:] == b"yyyy":
                    content = content[:-4]
                    bytes_data += content
                    received_bytes[seqnum] = content
                    if set_pb: set_pb(length, len(bytes_data))
                    break
                
                else:
                    bytes_data += content
                    received_bytes[seqnum] = content
                    
                    if set_pb: set_pb(length, len(bytes_data))

        udp_client.close()
        return b"".join(received_bytes.values())

    @classmethod
    def handle_dl(cls, client, args):
        """ handle download operation, to download a file from server 
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        def write_file(filename, bytes_data):
            """ write bytes data to the file 
                >>> @param:filename:    -> name of the file
                >>> @param:bytes_data:  -> data to be written, in the form of bytes
            """
            with open(filename, "wb") as f:
                f.write(bytes_data)

        client.send(OpCode.DL)
        resp = client.receive()
        if resp == OpCode.SI:
            filename = args.get("filename") 
            client.send(f'{filename}')
            resp = client.receive()
            if resp == OpCode.RST:
                return 'file not found or server failed to read file - try again'
            
            else:
                set_pb = args.get("set_pb", None)
                length = int(resp)
                client.send(OpCode.SI)
                udpclient, udpaddr = cls._init_udp_client()
                client.send(udpaddr)
                bytes_data = cls._receive_over_udp(length, udpclient, set_pb)
                write_file(args.get("localfile", filename), bytes_data)
                client.send(OpCode.ACK)
                return f'file [{filename}] downloaded from server'
        
        else:
            return "server is not ready to send file - try again"

    @classmethod
    def handle_cm(cls, client, args):
        """ handle CM operation, to send message to a client
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        client.send(OpCode.CM)
        resp = client.receive()
        
        if resp == OpCode.SI:
            target_client   = args.get("target_client")
            msg_str         = args.get("msg_str")
            client.send(target_client)
            resp = client.receive()
            if resp == OpCode.SI:
                client.send(msg_str)
                resp = client.receive()
                if resp == OpCode.ACK:
                    return "messages sent successfully"
                else:
                    return "server is failed to send messages - try again"
            else:
                return "server is not ready to receive messagaes - try again"
        
        else:
            return "server is not ready to send messages - try again"

    @classmethod
    def handle_acm(cls, client, args):
        """ handle ACM operation, to send message to all clients
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        client.send(OpCode.ACM)
        resp = client.receive()
        
        if resp == OpCode.SI:
            msg_str     = args.get("msg_str")
            client.send (msg_str)
            resp        = client.receive()
            if resp == OpCode.ACK:
                return "messages sent successfully"

            else:
                return "server is failed to send messages - try again"

        else:
            return "server is not ready to send messages - try again"


    @classmethod
    def handle_ccn(cls, client, args):
        """ handle ccn operation, to request connected client names
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> user input required to handle operation  
        """

        client.send(OpCode.CCN)
        resp = client.receive()
        return resp

    
class Client(): 
    """ module to enable client's communication with server  """
    def __init__(self, ui):
        """ class constructor
        """
        super(Client, self).__init__()
        self._client    = None
        self._STOP      = False   
        self.name       = ""
        self.ui         = ui
        self._port      = None

    @property
    def Connected(self):
        """ return True if client is connected, False otherwise """
        return True if self._client else False

    def _connect_with_available_port(self, serverip, port):

        for p in range(50001, 50016):
            try:
                self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._client.bind(("127.0.0.1", p))
                self._client.connect((serverip, port))
                self._port = p
            
            except Exception as e:
                continue

            resp = pickle.loads( self._client.recv(512) )
            if resp == OpCode.ACK:
                return True

        return False


    def connect(self, name, serverip='127.0.0.1', port=50000):
        """ connect with server at given ip & port
            >>> @param:name     -> name of user
            >>> @param:serverip -> ip address for server
            >>> @param:port     -> port at which server is listening 
        """
        try:
            
            
            if self._connect_with_available_port(serverip, port):
                self._client.send(pickle.dumps(name))
                result = pickle.loads( self._client.recv(512) )
                if result == OpCode.RST:
                    self._client = None
                    return False, "username already registered at server"
                
                else:
                    self.name = name
                    return True, "connection with server is made..."
            
            else:
                self._client = None
                return False, "Server Max Connection Limit: no port available for server connection"
        
        except Exception as e:
            self._client = None
            return False, "failed to connect - make sure server is running"

    def send(self, data):
        """ send request to the server, connected with
            >>> @param:data     -> data to be sent to the server
        """
        self._client.send(pickle.dumps(data))

    def is_message(self, datastr):
        """ return True if datastr is a message else False """
        try:    return True if ("msg_lst" in datastr or "MSG" in datastr) else False
        except: False

    def receive(self, bytes_len=4090, msg=False):
        """ receive message from server, connected with
            >>> @param:bytes_len-> length of byte data to be received from server
            >>> @param:msg      -> flag to mark receiving data as messages
        """
        data_str    = pickle.loads(self._client.recv(bytes_len) )
        while self.is_message(data_str):
            if len(data_str) > 4: 
                data_str = data_str.replace("MSG_", "")
                self.ui.set_log(f"{data_str}")
            
            if msg:
                break
            
            data_str = pickle.loads(self._client.recv(bytes_len))
        
        return data_str

    def close(self):
        """ close session with server """
        self._client.close()    

    def stop(self):
        """ stop client loop"""
        self._STOP = True


