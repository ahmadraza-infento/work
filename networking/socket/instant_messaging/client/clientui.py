
import os
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtUiTools
from utils import Client, Handler, OpCode
from datetime import datetime


def standard_dt():
    return datetime.now().strftime("%H:%M:%S %d-%m-%Y")


class Screens:
    AUTH            = 0
    SELECT_CLIENT   = 1
    CREATE_GROUP    = 2
    PROFILE         = 3


class MainApp(QStackedWidget):

    def __init__(self) -> None:
        super().__init__()
        self._forms             = {}
        self._new_group_users   = []
        self._profile_data      = {}
        self._profile_mode      = False
        self.setWindowTitle("Client Manager")
        Handler.init()
        self._client = Client(self)
        self._message_event = QTimer()
        self._message_event.timeout.connect(self._request_messages)
        self._message_event.start(1000)

    def _request_messages(self):
        """ request messages from server """
        if self._client.Connected:
            if self._profile_mode:
                data = Handler.handle(OpCode.PR, self._client, self._profile_data)
                self._add_profile_messages(data.get("messages", []), True)
            else:
                data = Handler.handle(OpCode.LST, self._client, {})
                self._update_combo_boxes(data)

    
    def _update_combo_boxes(self, data):
        self._forms['selectclient'].cmb_client.clear()
        self._forms['selectclient'].cmb_group.clear()
        self._forms['creategroup'].cmb_client.clear()
        self._forms['selectclient'].cmb_client.addItems(["-- Select User --"] + data['users'])
        self._forms['selectclient'].cmb_group.addItems(["-- Select Group --"] + data['groups'])
        data = [v.split('-->')[0].strip() if "-->" in v else v for v in data['users']]
        self._forms['creategroup'].cmb_client.addItems(["-- Select User --"] + data)

    def set_status(self, status, form):
        """ set status over ui form 
            >>> @param:status   -> str message to display
            >>> @param:form     -> one of available forms
        """
        self._forms[form].statusbar.setText(status)

    def set_log(self, log_text, form):
        """ set logs over text area over ui form 
            >>> @param:log_text -> str message to display over text edit area
            >>> @param:form     -> one of available forms ['creategroup', 'profile']
        """
        self._forms[form].te_logs.insertPlainText(f"--> {log_text} \n")
    
    def clear_log(self, form):
        """ clear log area over ui form 
            >>> @param:form -> one of available forms ['creategroup', 'profile']
        """
        self._forms[form].te_logs.clear()

    #region Auth
    def _init_auth(self):
        auth_class, authbase_class = QtUiTools.loadUiType("ui/auth.ui")
        self._forms['auth'] = authwin    = auth_class()
        authwidget = authbase_class()
        authwin.setupUi(authwidget)
        authwin.btn_login.clicked.connect(self._on_auth_login)
        authwin.btn_register.clicked.connect(self._on_auth_register)
        self.addWidget(authwidget)

    def _on_auth_login(self):
        text = self._forms['auth'].le_usename.text()
        if text == "":
            self.set_status("no username provided", 'auth')
        
        else:
            flag, result = self._client.connect(name=text, op=OpCode.LOGIN)
            if flag:
                self._current_user = result
                self._load_select_client()
            
            else:
                self.set_status(result, 'auth')

    def _on_auth_register(self):
        text = self._forms['auth'].le_usename.text()
        if text == "":
            self.set_status("no username provided", 'auth')
        
        else:
            flag, result = self._client.connect(name=text, op=OpCode.REGISTER)
            if flag:
                self._current_user = result
                self._load_select_client()
            
            else:
                self.set_status(result, 'auth')

    def _load_select_client(self):
        self.set_status     ("Select User or Group to View Messages", "selectclient")
        self.setCurrentIndex(Screens.SELECT_CLIENT)
        self.setWindowTitle (self._current_user.get('username')) 
        self._profile_mode  = False
    #endregion

    #region Select Client
    def _init_select_client(self):
        sc_class, scbase_class = QtUiTools.loadUiType("ui/select_client.ui")
        self._forms['selectclient'] = scwin = sc_class()
        scwidget        = scbase_class()
        scwin.setupUi   (scwidget)

        scwin.cmb_client.clear()
        scwin.cmb_group.clear()
        scwin.cmb_client.currentTextChanged.connect(self._cmb_client_changed)
        scwin.cmb_group.currentTextChanged.connect(self._cmb_group_changed)
        scwin.btn_new_group.clicked.connect(self._load_create_group)
        self.addWidget(scwidget)

    def _cmb_client_changed(self, value):
        if value not in ("", "-- Select User --"):
            self._load_profile(value, 0)

    def _cmb_group_changed(self, value):
        if value not in ("", "-- Select Group --"):
            self._load_profile(value, 1)

    def _load_create_group(self):
        self._clear_create_group("Add Group Users")
        self.setCurrentIndex(Screens.CREATE_GROUP)
        self.setWindowTitle (self._current_user.get('username')) 
     
    #endregion

    #region Create Group
    def _init_create_group(self):
        cg_class, cgbase_class                      = QtUiTools.loadUiType("ui/create_group.ui")
        self._forms['creategroup']                  = cgwin = cg_class()
        cgwidget                                    = cgbase_class()
        cgwin.setupUi                               (cgwidget)
        cgwin.btn_create_group.clicked.connect      (self._btn_create_group_clicked)
        cgwin.btn_back.clicked.connect              (self._load_select_client)
        cgwin.cmb_client.currentTextChanged.connect (self._cmbg_client_changed)
        self.addWidget                              (cgwidget)

    def _clear_create_group(self, status):
        """ clear create group state 
            >>> @param:status   -> status to be displayed
        """
        self.set_status(status, 'creategroup')
        self.clear_log('creategroup')
        self._new_group_users.clear()
        self._forms['creategroup'].le_groupname.setText("")

    def _cmbg_client_changed(self, value):
        if value not in ("", "-- Select User --"):
            if value in self._new_group_users:
                self._new_group_users.remove(value)
                self.clear_log("creategroup")
                for log in self._new_group_users:
                    self.set_log(log, "creategroup")
                
            else:
                self._new_group_users.append(value)
                self.set_log(value, "creategroup")

    def _btn_create_group_clicked(self):
        groupname = self._forms['creategroup'].le_groupname.text()
        if len(self._new_group_users) > 0 and groupname != "":
            flag = Handler.handle(OpCode.CG, self._client, {"groupname":groupname, 
                                                    "members":self._new_group_users})
            if flag:
                self._clear_create_group("Group Created Successfully")
            
            else:
                self._clear_create_group("Failed to Create Group")

        else:
            self.set_status("incomplete data provided", 'creategroup')
    
    #endregion

    #region Profile
    def _init_profile(self):
        pr_class, prbase_class  = QtUiTools.loadUiType("ui/profile.ui")
        self._forms['profile']  = prwin = pr_class()
        prwidget                = prbase_class()
        prwin.setupUi           (prwidget)

        prwin.btn_back.clicked.connect      (self._load_select_client)
        prwin.btn_send.clicked.connect      (self._send_message)
        prwin.btn_sendfile.clicked.connect  (self._send_file)
        self.addWidget                      (prwidget)

    def _clear_profile(self, status):
        """ clear profile state 
            >>> @param:status   -> status to be displayed
        """
        self.set_status(status, 'profile')
        self.clear_log('profile')
        self._forms['profile'].le_message.setText("")

    def _load_profile(self, name, type):
        self.setCurrentIndex    (Screens.PROFILE)
        self._profile_mode      = True
        name                    = name.split('-->')[0].strip()
        self._profile_data      = {"sender":name, "receiver":self._current_user['id'], "usertype":type}
        data                    = Handler.handle(OpCode.PR, self._client, self._profile_data) # {'name':name, 'type':type}
        status                  = data.get("status", "")
        status                  = name+ f"({status})" if status != "" else name+ "" 
        self._clear_profile     (status)
        self.setWindowTitle     (status + f" - {self._current_user['username']}")

        if data:
            self._add_profile_messages(data.get('messages', []))

    def _download_message(self, filename):
        """ return True, if file should be downloaded otherwise False """
        filepath = os.path.join(Handler._data_folder, f"{self._current_user['username']}_{filename}")
        if not os.path.exists(filepath):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Download File")
            dlg.setText(f"Would You Like to Download '{filename}'")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec_()

            return True if button == QMessageBox.Yes else False
        
        else:
            return False

    def _add_profile_messages(self, messages, clear=False):
        if clear and self._profile_data['usertype'] == 1:
            self.clear_log("profile")
        for m in messages:
            if m['type'] == 1:
                if self._download_message(m['message']):
                    Handler.handle(OpCode.DL, self._client, {"filename":m['message'], 'username':self._current_user['username']})
                    message = f"<{m['username']} : {m['messagedate']}> {m['message']}"
                    self.set_log(message, 'profile')
            else:
                username = m['username'] if m['username'] != self._current_user['username'] else "You"
                message = f"<{username} : {m['messagedate']}> {m['message']}"
                self.set_log(message, 'profile')

    def _send_message(self):
        message = self._forms['profile'].le_message.text()
        if message != "":
            packet = {'message':message, "sender":self._current_user['id'], 
                    'receiver':self._profile_data['sender'], "type":0}
            msgdt = packet['msgdt'] = standard_dt()
            flag = Handler.handle(OpCode.SM, self._client, packet)
            if flag:
                self.set_status("Message Sent", "profile")
                self.set_log(f"<You : {msgdt}> {message}", 'profile')
                self._forms['profile'].le_message.setText("")
            
            else:
                self.set_status("Message Sending Failed", "profile")

        else:
            self.set_status("No Message Provided", "profile")
    
    def _send_file(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
                        None,
                        "QFileDialog.getOpenFileName()",
                        "",
                        "All Files (*)",
                        options=options,
                    )
        
        packet = {'message':filepath, "sender":self._current_user['id'], 
                    'receiver':self._profile_data['sender'], "type":1}
        msgdt = packet['msgdt'] = standard_dt()
        flag = Handler.handle(OpCode.SF, self._client, packet)
        if flag:
            self.set_status("File Sent", "profile")
            self.set_log(f"<You : {msgdt}> {filepath}", 'profile')
            self._forms['profile'].le_message.setText("")
        
        else:
            self.set_status("File Sending Failed", "profile")

    #endregion
    
    def run(self):
        self._init_auth()
        self._init_select_client()
        self._init_create_group()
        self._init_profile()
        
        self.setFixedHeight(381)
        self.setFixedWidth(352)
        self.show()

       


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.run()

    try:
        sys.exit(app.exec_())
    except Exception:
        print("Exiting...")
