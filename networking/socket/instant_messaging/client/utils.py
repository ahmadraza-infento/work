import os
import socket
import pickle
from loges import Logger


Logger.init("client", logType="t")

class OpCode:
    """ Base module to represent operations codes"""
    # codes for internel server working
    RST         = "RST" # server will respond with RST, if wrong packet is received
    ACK         = "ACK" # acknowledgement
    SI          = "SI"  # send info, response if server needs more info

    # operations suported for client
    LST         = "LST" # list users, groups and messages
    DL          = "DL"  # download file
    SF          = "SF"
    CG          = "CG"  # Create Group
    PR          = "PR"  # Profile
    SM          = "SM"  # Send Message
    LOGIN       = "LOGIN"
    REGISTER    = "REGISTER"

    _opcodes    = ("RST", "ACK", "LST", "DL", "SM", "PR", "SF")
    _client_menu= ("LST", "DL", "SM", "CG", "PR", "SF")

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
    _data_folder = "./filesdir"
    if not os.path.exists(_data_folder):
        os.makedirs(_data_folder)

    @classmethod
    def init(cls):
        """ initialize the handlers for client operations """

        cls._handlers = {   
                            OpCode.LST      : cls.handle_lst,
                            OpCode.DL       : cls.handle_dl,
                            OpCode.SF       : cls.handle_sf,
                            OpCode.CG       : cls._handle_cg,
                            OpCode.PR       : cls.handle_pr,
                            OpCode.SM       : cls.handle_sm
                        }

    @classmethod
    def handle(cls, opcode, client, args):
        """ handle client input and pass the control to respective handler 
            >>> @param:opcode   -> operation code selected by client
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> user input required to handle operation 
        """
        
        if OpCode.valid_menu_op(opcode):
            if opcode not in  (OpCode.LST, OpCode.PR):
                Logger.info(f'handling [{opcode}] ')
            return cls._handlers[opcode](client, args)

        else:
            Logger.error(f"invalid menu opcode [{opcode}] selected")
            return f"invalid menu opcode [{opcode}] selected"

    @classmethod
    def request_messages(cls, client):
        """ request messages from server for active client 
        """
        client.send(OpCode.MSG)
        client.receive(msg=True)
    
    @classmethod
    def handle_lst(cls, client, args):
        """ handle LST operation, to list users and groups at server 
            >>> @param:client   -> an instance of client class
            @return:users, groups and messages associated with each user and group
        """
        
        client.send(OpCode.LST)
        resp = client.receive()
        return resp

    @classmethod
    def _handle_cg(cls, client, args):
        """ create a group from available users   
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> {"groupname":"", "members":[list of users]}
            @return:True or False
        """
        client.send(OpCode.CG)
        resp = client.receive()
        if resp == OpCode.SI:
            client.send(args)
            resp = client.receive()
            return True if resp == OpCode.ACK else False
        
        else:
            return False

    @classmethod
    def handle_pr(cls, client, args):
        """ load messages & active status for active profile   
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> {"sender":"name_of_sender", 
                                    "receiver":id of active user, 
                                    "usertype":0/1[IndividualUser/Group]}
            >>> @return:{"status":"online/offline", "messages":[{}, {}]}
        """
        client.send(OpCode.PR)
        resp = client.receive()

        if resp == OpCode.SI:
            client.send(args)
            resp = client.receive()
            return resp

        else:
            return {}        

    @classmethod
    def handle_sm(cls, client, args):
        """ send message fro active user to target user or group   
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> {'message':message, "sender":id_for_active_user, 
                                    'receiver':username for target group or user, 
                                    "type":0/1[IndividualUser/Group]}
            >>> @return:True or False
        """
        client.send(OpCode.SM)
        resp = client.receive()
        if resp == OpCode.SI:
            client.send(args)
            resp = client.receive()
            if resp == OpCode.ACK:
                return True
            
            else:
                return False
        
        else:
            return False
    
    @classmethod
    def handle_dl(cls, client, args):
        """ handle download operation, to download a file from server 
            >>> @param:client   -> an instance of client class 
            >>> @param:args     -> {"username":name of active user
                                    "filename":name of file to be downloaded}
            >>> @return: True or False 
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
                Logger.error('file not found or server failed to read file - try again')
                return False
            
            else:
                length = int(resp)
                client.send(OpCode.SI)
                bytes_data = client.receive(length, False) 
                filepath = os.path.join(cls._data_folder, f"{args['username']}_{filename}")
                write_file(filepath, bytes_data)
                client.send(OpCode.ACK)
                Logger.info(f'file [{filename}] downloaded from server')
                return True
        
        else:
            Logger.error("server is not ready to send file - try again")
            return False
 
    @classmethod
    def handle_sf(cls, client, args):
        """ send a file from user-user or in group
            >>> @param:client   -> an instance of client class
            >>> @param:args     -> {'message':path of file, "sender":id_for_active_user, 
                                    'receiver':username for target group or user, 
                                    "type":0/1[IndividualUser/Group]}
            >>> @return:True or False
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

        client.send(OpCode.SF)
        resp = client.receive()
        if resp == OpCode.SI:
            filepath = args.get("message", "")
            filename = filepath.split('/')[-1]
            if os.path.exists(filepath):
                bytes_data, length = read_file(filepath)
                args['length']  = length
                args['filename']= filename
                client.send(args)
                resp = client.receive()
                if resp == OpCode.SI:
                    client.send(bytes_data, True, False)
                    resp = client.receive()
                    
                    if resp == OpCode.ACK:
                        return True
                    else:
                        return False
                else:
                    return False
            
            else:
                return False
        else:
            return False


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

    

    @property
    def Connected(self):
        """ return True if client is connected, False otherwise """
        return True if self._client else False

    def connect(self, name, op, serverip='127.0.0.1', port=50000):
        """ connect with server at given ip & port
            >>> @param:name     -> name of user
            >>> @param:op       -> op code to establish connection, [LOGIN or REGISTER]
            >>> @param:serverip -> ip address for server
            >>> @param:port     -> port at which server is listening 
        """
        try:
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client.connect((serverip, port))
            self._client.send(pickle.dumps(f"{name}_{op}"))
            result = pickle.loads( self._client.recv(512) )
            if result == OpCode.RST:
                self._client = None
                message = "username already registered" if op == OpCode.REGISTER else "wrong username"
                return False, message
            
            else:
                self.name = name
                Logger.info("connection with server is made...")
                return True, result
        
        except Exception as e:
            Logger.exception(e, "connect")
            self._client = None
            return False, "failed to connect - try again"

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



# main code to run client
if __name__ == '__main__':

    Handler.init()
    server_ip   = '127.0.0.1'  
    server_port = 50000
    client      = Client()
    #client.connect(server_ip, server_port)  # creates a connection with the server
    client.run()
