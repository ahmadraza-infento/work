
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import safeqthreads
from utils import Client, Handler, OpCode

class AppSignals(QObject):
    logger = Signal(str)

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        Handler.init()
        self._client = Client(self)
        self._message_event = QTimer()
        self._message_event.timeout.connect(self._request_messages)
        self._message_event.start(1000)

    def _request_messages(self):
        """ request messages from server """
        if self._client.Connected:
            Handler.request_messages(self._client)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(490, 496)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.te_logsbar = QTextEdit(self.centralwidget)
        self.te_logsbar.setObjectName(u"te_logsbar")
        self.te_logsbar.setGeometry(QRect(20, 10, 451, 251))
        self.btn_connect = QPushButton(self.centralwidget)
        self.btn_connect.setObjectName(u"btn_connect")
        self.btn_connect.setGeometry(QRect(332, 270, 141, 41))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btn_connect.setFont(font)
        self.btn_connect.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_connect.setAutoDefault(False)
        self.btn_connect.setFlat(False)
        self.btn_connect.clicked.connect(self.connect)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 270, 141, 31))
        self.label.setFont(font)
        self.le_usename = QLineEdit(self.centralwidget)
        self.le_usename.setObjectName(u"le_usename")
        self.le_usename.setGeometry(QRect(130, 270, 181, 41))
        font1 = QFont()
        font1.setPointSize(12)
        self.le_usename.setFont(font1)
        self.cmb_menu = QComboBox(self.centralwidget)
        self.cmb_menu.addItem("")
        self.cmb_menu.addItem("")
        self.cmb_menu.addItem("")
        self.cmb_menu.addItem("")
        self.cmb_menu.addItem("")
        self.cmb_menu.addItem("")
        self.cmb_menu.setObjectName(u"cmb_menu")
        self.cmb_menu.setGeometry(QRect(130, 330, 341, 61))
        font2 = QFont()
        font2.setPointSize(14)
        self.cmb_menu.setFont(font2)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 350, 141, 31))
        self.label_2.setFont(font)
        self.btn_proceed = QPushButton(self.centralwidget)
        self.btn_proceed.setObjectName(u"btn_proceed")
        self.btn_proceed.setGeometry(QRect(330, 400, 141, 41))
        self.btn_proceed.setFont(font)
        self.btn_proceed.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_proceed.setAutoDefault(False)
        self.btn_proceed.setFlat(False)
        self.btn_proceed.clicked.connect(self.proceed)
        self.btn_reset = QPushButton(self.centralwidget)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setGeometry(QRect(130, 400, 141, 41))
        self.btn_reset.setFont(font)
        self.btn_reset.setStyleSheet(u"background-color:rgba(225,225,225,255);")
        self.btn_reset.setAutoDefault(False)
        self.btn_reset.setFlat(False)
        self.btn_reset.clicked.connect(self.reset)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 490, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.btn_connect.setDefault(False)
        self.btn_proceed.setDefault(False)
        self.btn_reset.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Client", None))
        self.btn_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"username:", None))
        self.cmb_menu.setItemText(0, QCoreApplication.translate("MainWindow", u"LST(List Files)", None))
        self.cmb_menu.setItemText(1, QCoreApplication.translate("MainWindow", u"DL(Download File)", None))
        self.cmb_menu.setItemText(2, QCoreApplication.translate("MainWindow", u"CM(Client Message)", None))
        self.cmb_menu.setItemText(3, QCoreApplication.translate("MainWindow", u"ACM(All Client Message)", None))
        self.cmb_menu.setItemText(4, QCoreApplication.translate("MainWindow", u"CCN(Connected Client Names)", None))
        self.cmb_menu.setItemText(5, QCoreApplication.translate("MainWindow", u"FIN(Finish)", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Menu:", None))
        self.btn_proceed.setText(QCoreApplication.translate("MainWindow", u"Proceed", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
    # retranslateUi
    
    def set_log(self, log_text):
        self.te_logsbar.insertPlainText(f"--> {log_text} \n")

    def connect(self):

        name = self.le_usename.text()
        flag, message = self._client.connect(name)
        if flag:
            self.set_log(message)
            self.btn_connect.setEnabled(False)

        else:
            self.set_log(message)

    def _input_dialog(self, header, input_name):
        text, ok = QInputDialog().getText(self, header, input_name, QLineEdit.Normal)
        if text and ok:
            return text
        else:
            return None

    def _input_messages(self):
        """ take messages from user as input """
        messages = []
        text = self._input_dialog("Message To Sent", "Message: ")
        if text:
            messages.append(text)
            while True:
                text = self._input_dialog("Message To Sent", "Message (cancel to exit): ")
                if text:
                    messages.append(text)
                else:
                    break
            msg_str = f'<msg_lst><{len(messages)}>'
            for msg in messages:
                msg_str += f'<"{msg}">'
            
            msg_str += '<end>'
            return msg_str

    def _take_input(self, op):
        """ take input from user for opcodes, where needed"""
        if op == OpCode.DL:
            text = self._input_dialog('File to Download', "File Name: ")
            if text:
                return {"filename":text}

        elif op == OpCode.CM:
            target_client = None
            while True:
                text = self._input_dialog('Target Client Name', "Client Name: ")
                if text:
                    if text == self._client.name:
                        self.set_log("invalid username")
                    else:
                        target_client = text
                        break
                else:
                    break
            
            if target_client:
                msg_str = self._input_messages()
                if msg_str:
                    return {"target_client":target_client, "msg_str":msg_str}

        elif op == OpCode.ACM:
            msg_str = self._input_messages()
            if msg_str:
                return {"msg_str":msg_str}
        
        else:
            return {}


        return None


    def proceed(self):
        if self._client.Connected:
            op  = self.cmb_menu.currentText().split("(")[0]
            args= self._take_input(op)
            if args is not None:
                result = Handler.handle(op, self._client, args)
                self.set_log(result)

        else:
            self.set_log("client not connected with server")

    def reset(self):
        self.te_logsbar.setText("")
        self.btn_connect.setEnabled(True)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_win = Ui_MainWindow()
    main_win.show()
    sys.exit(app.exec_())
