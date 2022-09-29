import os
import shutil
import pickle
import socket
from loges import Logger
from sqlite import SQLite
from threading import Thread

Logger.init("server_logs")
dbengine = SQLite("./", "serverdb.db")

class OpCode:
    """ Base module to represent operations codes """
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

    @classmethod
    def validate_opcode(cls, opcode):
        """ return True of opcode is a valid code else False 
            >>> @param:opcode   -> any opcode supported by OpCode
        """
        return True if opcode in cls._opcodes else False

    @classmethod
    def valid_admin_opcode(cls, opcode):
        """ return True if opcode is valid for admin only 
            >>> @param:opcode   -> any opcode supported by OpCode
        """
        return True if opcode in (cls.ST, cls.DU, cls.NU) else False

class Handler():
    """ Interface to handle current connected client"""
    _data_folder = "./userdata"
    
    @classmethod
    def init(cls):
        """ initialize handlers to respond to client requests """
        cls._handlers = {   OpCode.LOGIN    : cls.handle_login, 
                            OpCode.LST      : cls.handle_lst,
                            OpCode.UP       : cls.handle_up,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.NU       : cls.handle_nu,
                            OpCode.DU       : cls.handle_du,
                            OpCode.FIN      : cls.handle_fin,
                            OpCode.ST       : cls.handle_st
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
    def handle_login(cls, client):
        """ handle login request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        
        def verify_data(data):
            """ verify format of login data received from client
                >>> @param:data -> data string sentby client
            """
            try:
                data_list = data.split(":")
                if len(data_list) == 4:
                    return {"username":data_list[1], "password":data_list[3]}
                
                else:
                    Logger.error(f'invalid data format [{data}] received for LOGIN')
                    return None
            
            except Exception as e:
                Logger.exception(e, "verify_data", "handle_login")
                return None

        def set_incorrect_login(user):
            """ set incorrect access count to be access incorrect login count in ST
                >>> @param:user -> username given by client to login
            """

            if os.path.exists(cls._data_folder, user):
                file = os.path.join(*[cls._data_folder, user, "incorrect_count.txt"])
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        try     : count = int(f.readline())
                        except  : count = 0
                
                else:
                    count = 0
                
                with open(file, 'w') as f:
                    f.write(f"{count+1}")

        client.send(OpCode.LOGIN)
        data = verify_data( client.receive() )
        
        if data:
            w = f"username='{data['username']}' AND password='{data['password']}'"
            user = dbengine.read("user", "*", where=w, single=True)
            if user:
                Logger.info(f'client [{client._addr}] logged-in successfully')
                client.set_user(data['username'])
                client.send(OpCode.ACK)
            
            else:
                set_incorrect_login(data['username'])
                client.set_user(None)
                Logger.error(f"user not found [{client._addr}]")
                client.send(OpCode.RST)
        
        else:
            Logger.error(f"invalid log-on data format received from [{client._add}], [{data}]")
            client.send(OpCode.RST)

    @classmethod
    def handle_lst(cls, client):
        """ handle LST request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """ 
        
        if client.get_user:
            resp = f"******* [{client.get_user}](LST) *******\n"
            files= os.listdir(os.path.join(cls._data_folder, client.get_user))
            resp += "no file available" if len(files) == 0 else '\n'.join(files)
        
        else:
            resp = f"******* [No User](LST) *******\n"
            resp += 'not logged-in'
            Logger.error("user not logged-in")
        
        resp += "\n******* [END] *******"
        client.send(resp)

    @classmethod
    def handle_up(cls, client):
        """ handle UP request by client and upload requested file 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        
        def verify_data(data):
            """ verify format of UP data received from client
                >>> @param:data -> data string received from client to upload file
            """
            
            try:
                data_list = data.split("-")
                if len(data_list) == 2:
                    return {"filename":data_list[0], "length":int(data_list[1])}
                
                else:
                    Logger.error(f'invalid data format [{data}] received for UP')
                    return None
            
            except Exception as e:
                Logger.exception(e, "verify_data", "handle_login")
                return None
        
        def write_file(filename, bytes_data):
            """ write file i active client's directory at server 
                >>> @param:filename     -> name of file
                >>> @param:bytes_data   -> byte data to be written in file 
            """

            with open(filename, 'wb') as f:
                f.write(bytes_data)

        if client.get_user:
            user_folder = os.path.join(cls._data_folder, client.get_user)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            client.send(OpCode.SI)
            file_data = verify_data (client.receive() )
            if file_data:
                client.send(OpCode.SI)
                bytes_data  = client.receive(file_data['length'], False)
                try:
                    filename    = os.path.join(user_folder, file_data['filename']) 
                    write_file  (filename, bytes_data)
                    client.send(OpCode.ACK)
                except Exception as e:
                    Logger.exception(e, "handle_up")
                    client.send(OpCode.RST)
            
            else:
                client.send(OpCode.RST)
        
        else:
            client.send(OpCode.RST)

    @classmethod
    def handle_dl(cls, client):
        """ handle DL request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        def verify_data(data):
            """ verify format of DL data received from client
                >>> @param:data -> data string received from client to download file
            """
            try:
                data_list = data.split(":")
                if len(data_list) == 2:
                    return data_list[1]
                
                else:
                    Logger.error(f'invalid data format [{data}] received for UP')
                    return None
            
            except Exception as e:
                Logger.exception(e, "verify_data", "handle_login")
                return None

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

        if client.get_user:
            client.send(OpCode.SI)
            filename = verify_data( client.receive() )
            if filename:
                user = client.get_user
                file_path = os.path.join(*[cls._data_folder, client.get_user, filename])
                if os.path.exists(file_path):
                    bytes_data, length = read_file(file_path)
                    if bytes_data:
                        client.send(f'{length}')
                        resp = client.receive()
                        if resp == OpCode.SI:
                            client.send(bytes_data, sendall=True, serialize=False)
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

            else:
                client.send(OpCode.RST)

            
        else:
            Logger.error('cliet not logged-in')
            client.send(OpCode.RST)

    @classmethod
    def handle_st(cls, client):
        """ handle ST request from client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        def get_incorrect_login(user):
            """ read incorrect login attempts for active client 
                >>> @param:user -> username foractive client
            """
            user_folder = os.path.join(cls._data_folder, user)
            if os.path.exists(user_folder):
                file = os.path.join(user_folder, "incorrect_count.txt")
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        try     : count = int(f.readline())
                        except  : count = 0
                
                else:
                    count = 0
            
            else:
                count = 0
            
            return f"Incorrect Logins   : {count}\n"

        if client.get_user:
            user_folder = os.path.join(cls._data_folder, client.get_user)
            resp    = f"******* [{client.get_user}](ST) *******\n"
            files   = os.listdir(user_folder)
            resp    += f"Number of Files    : {len(files)}\n"
            total_size= sum([os.path.getsize(os.path.join(user_folder, file)) for file in files ])
            resp    += f"Total Size of Data : {total_size} bytes \n"
            resp    += get_incorrect_login(client.get_user)            
        
        else:
            resp = f"******* [No User](ST) *******\n"
            resp += 'not logged-in \n'
            Logger.error("user not logged-in")
        
        resp += "Server Runtime     : socket\n"
        
        resp += "******* [END] *******"

        client.send(resp)

    @classmethod
    def handle_du(cls, client):
        """ handle DU request by the user 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        def verify_data(data):
            """ verify format of du data received from client
                >>> @param:data -> data string received from client to delete a user
            """

            try:
                data_list = data.split(":")
                if len(data_list) == 2:
                    return data_list[1]
                
                else:
                    Logger.error(f'invalid data format [{data}] received for DU')
                    return None
            
            except Exception as e:
                Logger.exception(e, "verify_data", "handle_login")
                return None
        
        client.send(OpCode.DU)
        du_data = verify_data( client.receive() )

        if du_data:
            w   = f"username='{du_data}'"
            user= dbengine.read("user", "*", where=w, single=True)
            if user:
                if dbengine.remove("user", w):
                    Logger.info(f"user [{du_data}] removed successfully")
                    
                    try: 
                        shutil.rmtree( os.path.join(cls._data_folder, du_data) )
                        Logger.info(f"user [{du_data}] data directory removed")
                    
                    except Exception as e: 
                        Logger.exception(e, "handle_du")

                    client.send(OpCode.ACK)
                
                else:
                    Logger.error(f'failed to remove user [{du_data}]')
                    client.send(OpCode.RST)
            
            else:
                Logger.error(f'user [{du_data}] not found')
                client.send(OpCode.RST)
                                 
        else:
            client.send(OpCode.RST)

    @classmethod
    def handle_nu(cls, client):
        """ handle NU request by client
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """
        
        def verify_data(data):
            """ verify format of nu data received from client, to register new user
                >>> @param:data -> data string received from client to register new user
            """
            try:
                data_list = data.split(":")
                if len(data_list) == 6:
                    return {"username":data_list[1], "password":data_list[3], 'isadmin':data_list[5]}
                
                else:
                    Logger.error(f'invalid data format [{data}] received for NU')
                    return None
            
            except Exception as e:
                Logger.exception(e, "verify_data", "handle_login")
                return None
        
        client.send(OpCode.NU)
        nu_data = verify_data( client.receive() )

        if nu_data:
            if dbengine.save("user", nu_data):
                os.makedirs(os.path.join(cls._data_folder, nu_data['username']))
                Logger.info(f"new user saved successfully at server")
                client.send(OpCode.ACK)
            
            else:
                Logger.error("failed to save user")
                client.send(OpCode.RST)

        else:
            Logger.error(f"invalid data format received for NU from [{client._addr}]")
            client.send(OpCode.RST)

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

    def __init__(self, client, addr, **kwargs) -> None:
        """ initialize client interface for client connected with server 
            >>> @param:client   -> socket instance for connected client
            >>> @param:addr     -> address of connected client
        """
        super().__init__(**kwargs)
        
        self._client    = client
        self._addr      = addr
        self._STOP      = False
        self._USER      = None

    @property
    def get_user(self):
        """ return username if current client is logged-in, None otherwise"""
        return self._USER

    def set_user(self, user):
        """ set a user to save session for logged-in user
            >>> @param:user -> username for logged-in user
        """
        self._USER = user
    
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
        while self._STOP is False:
            request = self.receive()
            Handler.handle(request, self)
        
        Logger.info(f"session with client [{self._addr}] ended")
            
class Server():
    """ Core module for server """

    MAX_NUM_CONN = 10  # keeps 10 clients in queue

    def __init__(self, host="127.0.0.1", port=12000):
        """ initialize server using socket module
            >>> @param:host -> ip address for server
            >>> @param:port -> port to open by server to receive client request
        """
        
        super().__init__()
        self.host       = host
        self.port       = port
        self.server     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self._client_handlers   = {} 

    def _bind(self):
        """ bind server with provided host and port"""
        self.server.bind((self.host, self.port))

    def _listen(self):
        """ start listening for client requests """
        self.server.listen(self.MAX_NUM_CONN)
        Logger.info(f"Listening at {self.host}/{self.port} ")

    def _accept_clients(self):
        """ accept client request and start ClientInterface for individual client """

        while True:
            client, addr = self.server.accept()
            Logger.info(f"connection request received from {addr}")
            
            thread = ClientInterface(client, addr)
            thread.setDaemon(True)
            thread.start()
            Logger.info(f'connected with {addr}...')
            self._client_handlers[addr] = (thread, client)
        
    def run(self):
        """ entr point for server module """
        self._bind()
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    Handler.init()
    server = Server()
    server.run()
