from ctypes.wintypes import MSG
import socket
import pickle
import safeqthreads
from loges import Logger


Logger.init("client", logType="t")

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
    FIN         = "FIN" # finish working for connected client

    _opcodes    = ("RST", "ACK", "LST", "DL", 
                    "CM", "ACM", "CCN", "MSG", "FIN")
    _client_menu= ("LST", "DL", "CM", "ACM", "CCN", "MSG", "FIN")

    @classmethod
    def valid_menu_op(cls, opcode):
        """ return True if opcode is valid menu operation, False otherwise """

        return True if opcode in cls._client_menu else False

    @classmethod
    def print_menu(cls):
        """ print opcodes as formated string """
        _op_str = "******MENU******\n"
        for value in cls._client_menu:
            value = value + (len(value)-5)*" "
            _op_str += f"<<<{value}>>>\n" 
        
        _op_str += "******END*******\n"
        print(_op_str)

class Handler():
    """ interface to handle client input"""

    @classmethod
    def init(cls):
        """ initialize the handlers for client operations """

        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.CM       : cls.handle_cm,
                            OpCode.ACM      : cls.handle_acm,
                            OpCode.CCN      : cls.handle_ccn,
                            OpCode.FIN      : cls.handle_fin
                        }

    @classmethod
    def handle(cls, opcode, client, args):
        """ handle client input and pass the control to respective handler 
            >>> @param:opcode   -> operation code selected by client
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        if OpCode.valid_menu_op(opcode):
            Logger.info(f'handling [{opcode}] ')
            return cls._handlers[opcode](client, args)
            #_ = input("press enter to continue ...")

        else:
            Logger.error(f"invalid menu opcode [{opcode}] selected")
            return f"invalid menu opcode [{opcode}] selected"

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
    def _receive_over_udp(cls, length, port):
        """ receive udp packet over given port """
        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_client.bind(("127.0.0.1", port))
        bytes_data = udp_client.recv(length)
        udp_client.close()
        return bytes_data

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
            filename = args.get("filename") #input('enter name of file to be downloaded >>>')
            client.send(f'{filename}')
            resp = client.receive()
            if resp == OpCode.RST:
                Logger.error('file not found or server failed to read file - try again')
                return 'file not found or server failed to read file - try again'
            
            else:
                length = int(resp)
                client.send(OpCode.SI)
                bytes_data = cls._receive_over_udp(length, client.Port+1000) 
                write_file(filename, bytes_data)
                client.send(OpCode.ACK)
                Logger.info(f'file [{filename}] downloaded from server')
                return f'file [{filename}] downloaded from server'
        
        else:
            Logger.error("server is not ready to send file - try again")
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
                    Logger.info("messages sent successfully")
                    return "messages sent successfully"
                else:
                    Logger.error("server is failed to send messages - try again")
                    return "server is failed to send messages - try again"
            else:
                Logger.error("server is not ready to receive messagaes - try again")
                return "server is not ready to receive messagaes - try again"
        
        else:
            Logger.error("server is not ready to send messages - try again")
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
                Logger.info("messages sent successfully")
                return "messages sent successfully"

            else:
                #Logger.error("server is failed to send messages - try again")
                return "server is failed to send messages - try again"

        else:
            Logger.error("server is not ready to send messages - try again")
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

    @classmethod
    def handle_fin(cls, client, args):
        """ handle FIN operation, to finish session with server
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        client.send(OpCode.FIN)
        resp = client.receive()
        if resp == OpCode.ACK:
            client.stop()
            return "client disconnected successfully"

        else:
            Logger.error(f"invalid code [{resp}] received from server")
            return f"invalid code [{resp}] received from server"
        
 
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
    def Port(self):
        return self._port

    @property
    def Connected(self):
        """ return True if client is connected, False otherwise """
        return True if self._client else False

    def connect(self, name, serverip='127.0.0.1', port=50000):
        """ connect with server at given ip & port
            >>> @param:name     -> name of user
            >>> @param:serverip -> ip address for server
            >>> @param:port     -> port at which server is listening 
        """
        try:
            
            # To connect at valid server port
            flag = False
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
                    flag = True
                    break

            if flag:
                self._client.send(pickle.dumps(name))
                result = pickle.loads( self._client.recv(512) )
                if result == OpCode.RST:
                    Logger.error("username already registered at server")
                    Logger.error("connection refused by server")
                    self._client = None
                    return flag, "username already registered at server"
                
                else:
                    self.name = name
                    Logger.info("connection with server is made...")
                    return flag, "connection with server is made..."
            
            else:
                Logger.error("Server Max Connection Limit: no port available for server connection")
                self._client = None
                return "Server Max Connection Limit: no port available for server connection"
        
        except Exception as e:
            Logger.exception(e, "connect")
            self._client = None
            return False, "failed to connect - make sure server is running"

    def send(self, data, sendall=False, serialize=True):
        """ send request to the server, connected with
            >>> @param:data     -> data to be sent to the server
            >>> @param:sendall  -> flag to send all of the data in case large data
            >>> @param:serialize-> flag to serialize the data before sending to the server
        """
        serialized_data = pickle.dumps(data) if serialize else data

        if sendall:
            self._client.sendall(serialized_data)   

        else: 
            self._client.send(serialized_data)

    def is_message(self, datastr):
        """ return True if datastr is a message else False """
        try:    return True if ("msg_lst" in datastr or "MSG" in datastr) else False
        except: False

    def receive(self, bytes_len=4090, deserialize=True, msg=False):
        """ receive message from server, connected with
            >>> @param:bytes_len    -> length of byte data to be received from server
            >>> @param:deserialize  -> flag to deserialize data after receiving from server
        """
        data    = self._client.recv(bytes_len)
        data_str= pickle.loads(data) if deserialize else data
        while self.is_message(data_str):
            if len(data_str) > 4: 
                data_str = data_str.replace("MSG_", "")
                self.ui.set_log(f"client message -> {data_str}")
            
            if msg:
                break
            data    = self._client.recv(bytes_len)
            data_str= pickle.loads(data) if deserialize else data
        
        return data_str

    def close(self):
        """ close session with server """
        self._client.close()    

    def stop(self):
        """ stop client loop"""
        self._STOP = True



# main code to run client
if __name__ == '__main__':

    Handler.init()
    server_ip   = '127.0.0.1'  
    server_port = 50000
    client      = Client()
    #client.connect(server_ip, server_port)  # creates a connection with the server
    client.run()
