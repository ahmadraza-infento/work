
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from backend import Client, Handler, OpCode


class UiClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._forms             = {}
        self.setWindowTitle("Client")
        Handler.init()
        self._client = Client(self)
        self._message_event = QTimer()
        self._message_event.timeout.connect(self._request_messages)
        self._message_event.start(1000)
        self._init_client()
    
    def _request_messages(self):
        """ request messages from server """
        if self._client.Connected:
            Handler.request_messages(self._client)

    def set_log(self, log_text, form='client'):
        """ set logs over text area over ui form 
            >>> @param:log_text -> str message to display over text edit area
            >>> @param:form     -> one of available forms ['client' for now]
        """
        self._forms[form].te_logs.insertPlainText(f"{log_text} \n") 
    
    def clear_log(self, form='client'):
        """ clear log area over ui form 
            >>> @param:form -> one of available forms ['client' for now]
        """
        self._forms[form].te_logs.clear()

    def set_pb(self, total, curr):
        """ set progressbar status
            >>> @param:total    -> total value to be tracked
            >>> @param:curr     -> curr value
        """
        value = int( (curr/total)*100 )
        self.pb_filedownload.setValue(value)

    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(965, 726)
        self.te_logs = QTextEdit(Dialog)
        self.te_logs.setObjectName(u"te_logs")
        self.te_logs.setGeometry(QRect(10, 130, 951, 391))
        self.te_logs.setFocusPolicy(Qt.NoFocus)
        self.btn_login = QPushButton(Dialog)
        self.btn_login.setObjectName(u"btn_login")
        self.btn_login.setGeometry(QRect(10, 10, 111, 41))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_login.setFont(font)
        self.btn_login.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_login.setAutoDefault(False)
        self.btn_login.setFlat(False)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(130, 20, 61, 31))
        self.label.setFont(font)
        self.le_username = QLineEdit(Dialog)
        self.le_username.setObjectName(u"le_username")
        self.le_username.setGeometry(QRect(200, 10, 191, 41))
        font1 = QFont()
        font1.setPointSize(12)
        self.le_username.setFont(font1)
        self.le_username.setFocusPolicy(Qt.StrongFocus)
        self.le_address = QLineEdit(Dialog)
        self.le_address.setObjectName(u"le_address")
        self.le_address.setGeometry(QRect(490, 10, 191, 41))
        self.le_address.setFont(font1)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(400, 20, 81, 31))
        self.label_2.setFont(font)
        self.btn_showonline = QPushButton(Dialog)
        self.btn_showonline.setObjectName(u"btn_showonline")
        self.btn_showonline.setEnabled(False)
        self.btn_showonline.setGeometry(QRect(690, 10, 151, 41))
        self.btn_showonline.setFont(font)
        self.btn_showonline.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_showonline.setAutoDefault(False)
        self.btn_showonline.setFlat(False)
        self.btn_clear = QPushButton(Dialog)
        self.btn_clear.setObjectName(u"btn_clear")
        self.btn_clear.setGeometry(QRect(850, 10, 111, 41))
        self.btn_clear.setFont(font)
        self.btn_clear.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_clear.setAutoDefault(False)
        self.btn_clear.setFlat(False)
        self.btn_serverfiles = QPushButton(Dialog)
        self.btn_serverfiles.setObjectName(u"btn_serverfiles")
        self.btn_serverfiles.setEnabled(False)
        self.btn_serverfiles.setGeometry(QRect(10, 70, 261, 41))
        self.btn_serverfiles.setFont(font)
        self.btn_serverfiles.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_serverfiles.setAutoDefault(False)
        self.btn_serverfiles.setFlat(False)
        self.le_targetuser = QLineEdit(Dialog)
        self.le_targetuser.setObjectName(u"le_targetuser")
        self.le_targetuser.setGeometry(QRect(10, 550, 191, 41))
        self.le_targetuser.setFont(font1)
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 520, 151, 31))
        self.label_3.setFont(font)
        self.le_message = QLineEdit(Dialog)
        self.le_message.setObjectName(u"le_message")
        self.le_message.setGeometry(QRect(220, 550, 601, 41))
        self.le_message.setFont(font1)
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(220, 520, 151, 31))
        self.label_4.setFont(font)
        self.btn_send = QPushButton(Dialog)
        self.btn_send.setObjectName(u"btn_send")
        self.btn_send.setEnabled(False)
        self.btn_send.setGeometry(QRect(840, 550, 121, 41))
        self.btn_send.setFont(font)
        self.btn_send.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_send.setAutoDefault(False)
        self.btn_send.setFlat(False)
        self.btn_download = QPushButton(Dialog)
        self.btn_download.setObjectName(u"btn_download")
        self.btn_download.setEnabled(False)
        self.btn_download.setGeometry(QRect(840, 630, 121, 41))
        self.btn_download.setFont(font)
        self.btn_download.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_download.setAutoDefault(False)
        self.btn_download.setFlat(False)
        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(400, 600, 271, 31))
        self.label_5.setFont(font)
        self.le_serverfile = QLineEdit(Dialog)
        self.le_serverfile.setObjectName(u"le_serverfile")
        self.le_serverfile.setGeometry(QRect(10, 630, 371, 41))
        self.le_serverfile.setFont(font1)
        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 600, 151, 31))
        self.label_6.setFont(font)
        self.le_clientfile = QLineEdit(Dialog)
        self.le_clientfile.setObjectName(u"le_clientfile")
        self.le_clientfile.setGeometry(QRect(400, 630, 421, 41))
        self.le_clientfile.setFont(font1)
        self.pb_filedownload = QProgressBar(Dialog)
        self.pb_filedownload.setObjectName(u"pb_filedownload")
        self.pb_filedownload.setGeometry(QRect(10, 680, 411, 31))
        self.pb_filedownload.setValue(0)
        self.pb_filedownload.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Dialog)

        self.btn_login.setDefault(False)
        self.btn_showonline.setDefault(False)
        self.btn_clear.setDefault(False)
        self.btn_serverfiles.setDefault(False)
        self.btn_send.setDefault(False)
        self.btn_download.setDefault(False)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.te_logs.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.btn_login.setText(QCoreApplication.translate("Dialog", u"Login", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"name", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"address", None))
        self.btn_showonline.setText(QCoreApplication.translate("Dialog", u"Show Online", None))
        self.btn_clear.setText(QCoreApplication.translate("Dialog", u"Clear", None))
        self.btn_serverfiles.setText(QCoreApplication.translate("Dialog", u"Show Server Files", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"To (blank to all)", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Message", None))
        self.btn_send.setText(QCoreApplication.translate("Dialog", u"Send", None))
        self.btn_download.setText(QCoreApplication.translate("Dialog", u"Download", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Client File Name (save as...)", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Server File Name", None))
    # retranslateUi

    #region Client
    def _init_client(self):
        self._forms['client']   = self
        self.le_username.setFocus()
        self.btn_login.clicked.connect       (self._on_login)
        self.btn_showonline.clicked.connect  (self._on_showonline)
        self.btn_clear.clicked.connect       (self._on_clear)
        self.btn_serverfiles.clicked.connect (self._on_serverfiles)
        self.btn_send.clicked.connect        (self._on_send)
        self.btn_download.clicked.connect    (self._on_download)
    
    def _enable_menu(self, enable=True):
        self._forms['client'].btn_showonline.setEnabled (enable)
        self._forms['client'].btn_serverfiles.setEnabled(enable)
        self._forms['client'].btn_send.setEnabled       (enable)
        self._forms['client'].btn_download.setEnabled   (enable)
    
    def _enable_login(self, enable=True):
        self._forms['client'].btn_clear.setEnabled (enable)
        self._forms['client'].btn_login.setEnabled(enable)

    def _on_login(self):
        """ login button handler """
        username = self._forms['client'].le_username.text() 
        serverip = self._forms['client'].le_address.text()
        
        flag, message = self._client.connect(username, serverip)
        if flag:
            self.set_log("connection established successfully")
            self._enable_menu()
            self._enable_login(False)
        
        else:
            self.set_log(message)
        
    def _on_showonline(self):
        """ show online button handler """
        resp = Handler.handle(OpCode.CCN, self._client)
        self.set_log(resp)
    
    def _on_clear(self):
        """ clear button handler """
        self._forms['client'].le_username.setText("") 
        self._forms['client'].le_address.setText("")

    def _on_serverfiles(self):
        """ Server Files button handler """
        resp = Handler.handle(OpCode.LST, self._client)
        self.set_log(resp)

    def _on_send(self):
        """ clear button handler """
        def clear_fields():
            self._forms['client'].le_targetuser.setText("")
            self._forms['client'].le_message.setText("")

        targetuser  = self._forms['client'].le_targetuser.text()
        message     = self._forms['client'].le_message.text()
        if message != "":
            if targetuser == "":
                msg = Handler.handle(OpCode.ACM, self._client, {"msg_str":message})
            else:
                msg = Handler.handle(OpCode.CM, self._client, {"target_client":targetuser, "msg_str":message})
            self.set_log(msg)
            clear_fields()
        else:
            self.set_log("[ERROR] please enter message")

    def _on_download(self):
        """ Server Files button handler """
        def clear_fields():
            self._forms['client'].le_serverfile.setText("")
            self._forms['client'].le_clientfile.setText("")

        self.pb_filedownload.setValue(0)
        filename = self._forms['client'].le_serverfile.text()
        localfile= self._forms['client'].le_clientfile.text()
        localfile= filename if localfile == "" else localfile
        
        if filename != "":
            message = Handler.handle(OpCode.DL, self._client, 
                        {"filename":filename, "localfile":localfile, "set_pb":self.set_pb})
            self.set_log(message)
            clear_fields()

        else:
            self.set_log("[ERROR] please enter filename")
    #endregion 


if __name__ == "__main__":
    app     = QApplication(sys.argv)
    main_win= UiClient()
    main_win.show()
    sys.exit(app.exec_())