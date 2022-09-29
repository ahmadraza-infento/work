from fileinput import filename
import os
import pickle
import socket

from loges import Logger
import safeqthreads
from threading import Thread
from sqlite import SQLite

dbengine = SQLite.get_driver('./', 'server.db')
Logger.init("server_logs", debug_mode=True)

class OpCode:
    """ Base module to represent operations codes """
    # codes for internel server working
    RST         = "RST" # server will respond with RST, if wrong packet is received
    ACK         = "ACK" # acknowledgement 
    SI          = "SI"  # send info, response if server needs more info
    
    # operations suported for client
    LST         = "LST" # list files
    SF          = "SF"  # Send File
    DL          = "DL"  # download file
    CG          = "CG"  # Create Group
    PR          = "PR"  # Profile
    SM          = "SM"  # Send Message
    LOGIN       = "LOGIN"
    REGISTER    = "REGISTER"

    _opcodes    = ("RST", "ACK", "LST", "DL", "SM", "CG", "PR", "SF")
    _client_menu= ("LST", "DL", "SM", "CG", "PR", "SF")

    @classmethod
    def validate_opcode(cls, opcode):
        """ return True of opcode is a valid code else False 
            >>> @param:opcode   -> any opcode supported by OpCode
        """
        return True if opcode in cls._opcodes else False

class UserType:
    USER = 0
    GROUP= 1

class MessageType:
    STR = 0
    FILE= 1

class MessageStatus:
    UNREAD  = 0
    READ    = 1

class Handler():
    """ Interface to handle current connected client"""
    _data_folder = "./filesdir"
    if not os.path.exists(_data_folder):
        os.makedirs(_data_folder)
    
    @classmethod
    def init(cls):
        """ initialize handlers to respond to client requests """
        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.SF       : cls.handle_sf,
                            OpCode.CG       : cls.handle_cg,
                            OpCode.PR       : cls.handle_pr,
                            OpCode.SM       : cls.handle_sm
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
            client.send(OpCode.RST)

    @classmethod
    def handle_lst(cls, client):
        """ handle LST request by client 
            >>> @param:client   -> ClientInterface instance, represents to current 
                                    connected client
        """ 
        
        users = dbengine.read("user", "*", where=f"type=0 AND id !={client.ClientID}")
        usermsgs       = dbengine.execute_select(f"""SELECT senderid as id, user.username, 
                                                sum(CASE WHEN status=0 Then 1 ELSE 0 END) as msgcount 
                                                FROM usermessage JOIN user ON usermessage.senderid=user.id  
                                                WHERE receiverid = {client.ClientID} GROUP BY senderid """, True) 
        usermsgs = {u['id']:u for u in usermsgs}
        
        for u in users:
            tmp = usermsgs.get(u['id'], None)
            u['msgcount'] = tmp['msgcount'] if tmp else 0
        
        usergroups  = dbengine.read('groupuser', ['groupid'], where=f"userid={client.ClientID}")
        if len(usergroups) > 0:
            usergroups  = ", ".join([str(ug['groupid']) for ug in usergroups] )
            groups      = dbengine.execute_select(f""" SELECT user.id, user.username, 
                                                    sum(CASE WHEN usermessage.status=0 THEN 1 ELSE 0 END) as msgcount 
                                                    FROM user LEFT JOIN usermessage 
                                                    ON user.id == usermessage.receiverid 
                                                    WHERE user.type == {UserType.GROUP} 
                                                    AND user.id in ({usergroups})
                                                    GROUP By usermessage.receiverid""", True)
        
        else:
            groups = []

        users = [f'{u["username"]} --> {u["msgcount"]}' for u in users]
        groups= [f'{g["username"]} --> {g["msgcount"]}' for g in groups]
        client.send({"users":users, "groups":groups}) 

    @classmethod
    def handle_cg(cls, client):
        client.send(OpCode.SI)
        data = client.receive()
        group= dbengine.read("user", "*", where=f"username='{data['groupname']}'", single=True)
        if group:
            client.send(OpCode.RST)
        
        else:
            if dbengine.save("user", {"username":data["groupname"], "type":UserType.GROUP}):
                group= dbengine.read("user", "*", where=f"username='{data['groupname']}'", single=True)
                members= ", ".join([f"'{m}'" for m in data["members"] ])
                members= dbengine.read("user", "*", where=f"username in ({members})")
                for m in members:
                    dbengine.save("groupuser", {"groupid":group["id"], "userid":m['id']})
                dbengine.save("groupuser", {"groupid":group["id"], "userid":client.ClientID})
                client.send(OpCode.ACK)

            else:
                client.send(OpCode.RST)
    
    @classmethod
    def handle_pr(cls, client):
        client.send(OpCode.SI)
        data = client.receive()  
        
        status= "" if data['usertype'] == UserType.GROUP else Server.is_active(data['sender'])
        sender = dbengine.read("user", "*", where=f"username='{data['sender']}'", single=True)
        if data['usertype'] == UserType.GROUP:
            messages= dbengine.execute_select(f"""SELECT um.id, u.username, um.message, 
                                            um.messagedate, um.type 
                                            FROM usermessage as um JOIN user as u 
                                            ON um.senderid = u.id 
                                            WHERE um.receiverid = {sender['id']} 
                                            AND um.status = {MessageStatus.UNREAD}""", True)
            if len(messages) > 0 :
                client.send({"messages":messages, "status":status})
                return
        else:
            
            if sender:
                messages= dbengine.execute_select(f"""SELECT um.id, u.username, um.message, 
                                                    um.messagedate, um.type 
                                                    FROM usermessage as um JOIN user as u 
                                                    ON um.senderid = u.id 
                                                    WHERE um.receiverid = {data['receiver']}
                                                    AND um.senderid = {sender['id']}  
                                                    AND um.status = {MessageStatus.UNREAD}""", True)
                msgids  = ", ".join([str(m['id']) for m in messages])

                if len(messages) > 0 :
                    dbengine.execute_update(f"UPDATE usermessage SET status = {MessageStatus.READ} WHERE id in ({msgids})")
                    client.send({"messages":messages, "status":status})
                    return 
            
        client.send({"messages":[], "status":status})

    @classmethod
    def _save_message(cls, data, client):
        receiver= dbengine.read("user", "*", where=f"username='{data['receiver']}'", single=True)
        if receiver:
            message = {"senderid":client.ClientID, "receiverid":receiver['id'], 
                        "message":data['message'], "messagedate":data['msgdt'], 
                        "type":data['type'] }
            if dbengine.save("usermessage", message):
                client.send(OpCode.ACK)
                Logger.info(f"message '{message}' sent to {receiver} by {client.ClientID}")
            
            else:
                client.send(OpCode.RST)
        
        else:
            client.send(OpCode.RST)

    @classmethod
    def handle_sm(cls, client):
        client.send(OpCode.SI)
        data = client.receive()
        cls._save_message(data, client)
        
    
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
                    client.send(bytes_data, True, False)
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
    def handle_sf(cls, client):

        def write_file(filename, bytes_data):
            """ write bytes data to the file 
                >>> @param:filename:    -> name of the file
                >>> @param:bytes_data:  -> data to be written, in the form of bytes
            """
            with open(filename, "wb") as f:
                f.write(bytes_data)
        
        client.send(OpCode.SI)
        data    = client.receive()
        length  = data['length']
        filename= data['filename']
        client.send(OpCode.SI)
        bytes_data = client.receive(int(length), False)
        filepath = os.path.join(cls._data_folder, filename)
        try:
            write_file(filepath, bytes_data)
            data['message'] = data['filename']
            cls._save_message(data, client)
        except:
            client.send(OpCode.RST)


class ClientInterface(Thread):
    """ module to handle client connected with server """

    def __init__(self, client, addr, detail, **kwargs) -> None:
        """ initialize client interface for client connected with server 
            >>> @param:client   -> socket instance for connected client
            >>> @param:addr     -> address of connected client
            >>> @param:name     -> detail of connected client
        """
        super().__init__(**kwargs)
        
        self._client    = client
        self._addr      = addr
        self._detail    = detail
        self._STOP      = False
        self._USER      = None

    @property
    def Port(self):
        return self._addr[1]

    @property
    def ClientName(self):
        """ return name of connected client"""
        return self._detail['username']
    
    @property
    def ClientID(self):
        """ return id of connected client """
        return self._detail['id']

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
            Server.on_client_disconnected(self.ClientName, self._addr)
            Logger.info(f"session with client [{self._addr}] ended")
            
class Server(safeqthreads.SafeWorker):
    """ Core module for server """

    MAX_NUM_CONN= 10  # keeps 10 clients in queue
    _self       = None

    @classmethod
    def init(cls, thread, signal, host, port, ui):
        cls._self = Server(thread, signal, host, port, ui)
        return cls._self

    #region Helpers
    @classmethod
    def is_active(cls, name):
        """ return online if client is active else offline 
            >>> @param:name -> name of user
        """
        return "online" if name in cls._self._client_handlers.keys() else "offline"

    @classmethod
    def connected_clients(cls):
        """ return name of all connected clients as list """
        return list( cls._self._client_handlers.keys() )
    
    @classmethod
    def on_client_disconnected(cls, name, addr):
        """ callback to be called when a client is disconnected
            >>> @param:name -> name of client
            >>> @param:addr -> address of client
        """
        self = cls._self
        self._client_handlers.pop(name, None)
        self.ui_signal.info.emit(f"{len(self.connected_clients())}")
    #endregion


    def __init__(self, thread, signal, host, port, ui):
        """ initialize server using socket module
            >>> @param:host         -> ip address for server
            >>> @param:port         -> port to open by server to receive client request
            >>> @param:ui           -> ui instance to set server logs
        """
         # create instance of super class of the Server
        super(Server, self).__init__(thread)
        
        self.host               = host
        self.port               = port
        self.server             = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self._client_handlers   = {} 
        self._ui                = ui
        self.ui_thread          = thread
        self.ui_signal          = signal

    def _bind(self):
        """ bind server with provided host and port"""
        self.server.bind((self.host, self.port))

    def _listen(self):
        """ start listening for client requests """
        self.server.listen(self.MAX_NUM_CONN)
        Logger.info(f"Listening at {self.host}/{self.port} ")
        self.ui_signal.logger.emit(f"Listening at {self.host}/{self.port} ")


    def _validate_user(self, client):
        """ receive and validate username from client"""
        data = pickle.loads( client.recv(512) )
        name, optype = data.split("_")
        user = dbengine.read("user", "*", where=f"username='{name}' and type={UserType.USER}", single=True)
        if user:
            if optype == OpCode.LOGIN:
                client.send(pickle.dumps(user))
            else:
                client.send(pickle.dumps(OpCode.RST))
                return None, "username already registered"
        
        else:
            if optype == OpCode.LOGIN:
                client.send(pickle.dumps(OpCode.RST) )
                return None, "wrong username"
            
            else:
                # register this new user
                user = {"username":name}
                if dbengine.save("user", user):
                    user = dbengine.read("user", "*",
                                where=f"username='{name}'", single=True)
                    client.send(pickle.dumps(user ))
                else:
                    client.send(pickle.dumps(OpCode.RSTs) )
                    return None, f"failed to register '{name}'"

        return user, ''
        
    def _init_client_interface(self, client, addr, detail):
        """ initialize interface to handle client requests 
            >>> @param:client   -> socket instance for client
            >>> @param:addr     -> address of connected client
            >>> @param:detail   -> detail connected client
        """

        thread = ClientInterface(client, addr, detail)
        thread.setDaemon(True)
        thread.start()
        self._client_handlers[detail['username']] = (thread, client)

    def _accept_clients(self):
        """ accept client request and start ClientInterface for individual client """

        while True:
            client, addr    = self.server.accept()
            Logger.info     (f"connection request received from {addr}")
            self.ui_signal.logger.emit(f"connection request received from {addr}")
            
            detail, message = self._validate_user(client)
            if detail:
                self._init_client_interface(client, addr, detail)
                self.ui_signal.info.emit(f"{len(self.connected_clients())}")
            else:
                Logger.info(f"Connection Refused[{addr}]: {message}")
                self.ui_signal.logger.emit(f"Connection Refused[{addr}]: {message}")
            
    def run(self):
        """ entr point for server module """
        self._bind()
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    Handler.init()
    Server.init(host="127.0.0.1", port=50000, port_range=range(50001, 50016))
