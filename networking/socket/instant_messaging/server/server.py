
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import safeqthreads
from utils import Handler, Server


class AppSignals(QObject):
    logger          = Signal(str)
    info            = Signal(str)

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._init_server()
        
    def _init_server(self):
        Handler.init()
        _signal = self._signal = AppSignals()
        _signal.logger.connect(self.set_log)
        _signal.info.connect(self.set_info)
        th =  safeqthreads.SafeQThread()

        bgWorker = Server.init(th, _signal, host="127.0.0.1", port=50000, ui=self)
        bgWorker.moveToThread(th)
        th.started.connect(bgWorker.run)
        th.start() 
        self._bg_worker = {'worker':bgWorker, 'thread':th} 

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(493, 407)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.te_logsbar = QTextEdit(self.centralwidget)
        self.te_logsbar.setObjectName(u"te_logsbar")
        self.te_logsbar.setGeometry(QRect(20, 10, 451, 251))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 280, 201, 31))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.lbl_clients = QLabel(self.centralwidget)
        self.lbl_clients.setObjectName(u"lbl_clients")
        self.lbl_clients.setGeometry(QRect(230, 280, 141, 31))
        self.lbl_clients.setFont(font)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 320, 201, 31))
        self.label_2.setFont(font)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 493, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Server", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Clients Connected:", None))
        self.lbl_clients.setText(QCoreApplication.translate("MainWindow", u"0", None))
    # retranslateUi

    def set_info(self, info):
        self.set_connected_clients(info)


    def set_log(self, log_text):
        self.te_logsbar.insertPlainText(f"--> {log_text} \n")

    def set_connected_clients(self, count):
        self.lbl_clients.setText(f"{count}")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_win = Ui_MainWindow()
    main_win.show()
    sys.exit(app.exec_())
