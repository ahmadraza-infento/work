import os
import socket
import pickle
from loges import Logger

Logger.init("client", logType="t")

class OpCode:
    """ Base module to represent operations codes"""
    RST         = "RST"
    ACK         = "ASK"
    SI          = "SI"
    LOGIN       = "LOGIN"

    LST         = "LST"
    UP          = "UP"
    DL          = "DL"

    # admin commands
    ST          = "ST"
    NU          = "NU"
    DU          = "DU"

    FIN         = "FIN"
    _opcodes    = ("RST", "ACK", "SI", "LOGIN", "LST", "UP", "DL", 
                    "ST", "NU", "DU", "FIN")
    _client_menu= ("LOGIN", "LST", "ST", "UP", "DL", 
                    "ST", "NU", "DU", "FIN")

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

        cls._handlers = {   OpCode.LOGIN    : cls.handle_login, 
                            OpCode.LST      : cls.handle_lst,
                            OpCode.ST       : cls.handle_st,
                            OpCode.UP       : cls.handle_up,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.NU       : cls.handle_nu,
                            OpCode.DU       : cls.handle_du,
                            OpCode.FIN      : cls.handle_fin
                        }

    @classmethod
    def handle(cls, opcode, client):
        """ handle client input and pass the control to respective handler 
            >>> @param:opcode   -> operation code selected by client
            >>> @param:client   -> an instance of client class 
        """
        
        if OpCode.valid_menu_op(opcode):
            Logger.info(f'handling [{opcode}] ')
            cls._handlers[opcode](client)
            _ = input("press enter to continue ...")

        else:
            Logger.error(f"invalid menu opcode [{opcode}] selected")

    @classmethod
    def handle_login(cls, client):
        """ handler login operation, to log-on server 
            >>> @param:client   -> an instance of client class 
        """

        client.send(OpCode.LOGIN)
        data = client.receive()

        if data == OpCode.LOGIN:
            username    = input("enter username >>>")
            password    = input('enter password >>>')
            logon_data  = f"USER:{username}:PASS:{password}"
            client.send(logon_data)
            data = client.receive()
            if data == OpCode.ACK:
                Logger.info("logged in successfully - you can continue further")

            else:
                Logger.error(f'faild to log-in - try again with correct credentials')

        else:
            Logger.error(f"invalid response [{data}] received from server - try again")


    @classmethod
    def handle_lst(cls, client):
        """ handle LST operation, to list files at server 
            >>> @param:client   -> an instance of client class 
        """
        
        client.send(OpCode.LST)
        resp = client.receive()
        print(resp)

    @classmethod
    def handle_up(cls, client):
        """ handle UP operation, to upload a file at server
            >>> @param:client   -> an instance of client class 
        """
        
        def read_file(filename):
            """ read file given file name
                >>> @param:filename -> name of file
            """
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    bytes_data = f.read()
                
                return bytes_data, len(bytes_data)

            else:
                return (None, 0)


        client.send(OpCode.UP)
        resp = client.receive()

        if resp == OpCode.SI:
            filename            = input('enter filename >>>')
            bytes_data, length  = read_file(filename)
            client.send(f'{filename}-{length}')
            res = client.receive()
            if res == OpCode.SI:
                client.send(bytes_data, sendall=True, serialize=False)
                resp = client.receive()
                if resp == OpCode.ACK:
                    Logger.info(f'file [{filename}] uploaded successfully')

                else:
                    Logger.error(f"file uploading failed - try again")
            
            else:
                Logger.error("server declined file upload - try again")
        
        else:
            Logger.error("server is not ready to upload file- try again")

    @classmethod
    def handle_dl(cls, client):
        """ handle download operation, to download a file from server 
            >>> @param:client   -> an instance of client class 
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
            filename = input('enter name of file to be downloaded >>>')
            client.send(f'DL:{filename}')
            resp = client.receive()
            if resp == OpCode.RST:
                Logger.error('file not found or server failed to read file - try again')
            
            else:
                length = int(resp)
                client.send(OpCode.SI)
                bytes_data = client.receive(length, deserialize=False)
                write_file(filename, bytes_data)
                client.send(OpCode.ACK)
                Logger.info(f'file [{filename}] downloaded from server')

        else:
            Logger.error("rejected by server - log-in to server")

    @classmethod
    def handle_st(cls, client):
        """ handle ST operation, to request stastics from server
            >>> @param:client   -> an instance of client class 
        """
        client.send(OpCode.ST)
        resp = client.receive()
        print(resp)

    @classmethod
    def handle_du(cls, client):
        """ handle DU operation, to delete a user at server
            >>> @param:client   -> an instance of client class 
        """
        client.send(OpCode.DU)
        resp = client.receive()

        if resp == OpCode.DU:
            user    = input("enter username to be removed >>>")
            du_data = f"DU:{user}"
            client.send(du_data)
            resp = client.receive()

            if resp == OpCode.ACK:
                Logger.info(f'user [{user}] removed successfully')

            else:
                Logger.error(f'unable to delete user - try again with correct username ') 
        
        else:
            Logger.error('server is not ready to delete user - try again')

    @classmethod
    def handle_nu(cls, client):
        """ handle NU operation, to create new user at server
            >>> @param:client   -> an instance of client class 
        """
        def read_input():
            """ prompt for input from user at command line"""
            username = input("enter username    >>>")
            while True:
                password = input("enter password    >>>")
                password1= input("re-enter password >>>")
                if password == password1:
                    is_admin= int(input("are you an admin (0/1) ?>>>"))
                    break
                else:
                    Logger.error('password not matched - enter same password')
            
            return username, password, is_admin

        client.send(OpCode.NU)
        resp = client.receive()
        if resp == OpCode.NU:
            username, passwd, is_admin = read_input()
            nu_data = f"USER:{username}:PASS:{passwd}:ADMIN:{is_admin}"
            client.send(nu_data)
            resp = client.receive()
            if resp == OpCode.ACK:
                Logger.info("new user registered successfully")
            
            else:
                Logger.error("failed create new user - try again")
        
        else:
            Logger.error("server is not ready to create new user - try again") 

    @classmethod
    def handle_fin(cls, client):
        """ handle FIN operation, to finish session with server
            >>> @param:client   -> an instance of client class 
        """
        client.send(OpCode.FIN)
        data = client.receive()
        if data == OpCode.ACK:
            client.stop()

        else:
            Logger.error(f"invalid code [{data}] received from server")
        

    
class Client():
    """ module to enable client's communication with server  """
    def __init__(self):
        """ class constructor
        """
        super().__init__()
        self._client    = None
        self._STOP      = False              

    def connect(self, serverip='127.0.0.1', port=12000):
        """ connect with server at given ip & port
            >>> @param:serverip -> ip address for server
            >>> @param:port     -> port at which server is listening 
        """
        try:
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client.connect((serverip, port))
            Logger.info("connection with server is made...")

        except Exception as e:
            Logger.exception(e, "connect")
            self._client = None

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

    def receive(self, bytes_len=4090, deserialize=True):
        """ receive message from server, connected with
            >>> @param:bytes_len    -> length of byte data to be received from server
            >>> @param:deserialize  -> flag to deserialize data after receiving from server
        """
        data    = self._client.recv(bytes_len)
        data_str= pickle.loads(data) if deserialize else data
        return data_str

    def close(self):
        """ close session with server """
        self._client.close()    

    def stop(self):
        """ stop client loop"""
        self._STOP = True

    def run(self):
        """entry point for this class, it will maintain the loop till stop() 
            is not called
        """
        
        if self._client:
            while self._STOP is False:
                OpCode.print_menu()
                opcode = input("enter opcode to proceed >>>")
                Handler.handle(opcode, self)
            
            self.close()

        else:
            Logger.error("client is not connected ... exiting")



# main code to run client
if __name__ == '__main__':

    Handler.init()
    server_ip   = '127.0.0.1'  
    server_port = 12000
    client      = Client()
    client.connect(server_ip, server_port)  # creates a connection with the server
    client.run()
