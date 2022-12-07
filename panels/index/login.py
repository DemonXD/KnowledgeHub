import string
import nanoid
from uuid import getnode

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QPushButton, QGridLayout, QLabel,
    QLineEdit, QWidget
)

from panels import BaseWindow, LoginStatus
from crud.user import check_user


class LoginWindow(BaseWindow):
    login_status = pyqtSignal(str)
    login_msg = pyqtSignal(str)
    def __init__(self):  
        super().__init__()
        self.mac = getnode() or nanoid.generate(string.ascii_letters, 16)
        self.setFixedSize(320, 240)
        self.setWindowTitle('Login')
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint)
        
        self.center()
        self.initUI()
        self.main_layout.setSpacing(0)
    
    def initUI(self):
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        # Login 标签部件
        self.label_widget = QWidget()
        self.label_widget.setObjectName("Login标签")
        self.label_layout = QGridLayout()
        self.label_widget.setLayout(self.label_layout)

        self.label = QLabel(str("登 陆"))
        font = self.label.font()
        font.setBold(True)
        font.setPointSize(26)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label_layout.addWidget(self.label)

        # 账号密码部件
        self.form_widget = QWidget()
        self.form_widget.setObjectName("账号密码区域")
        self.form_layout = QGridLayout()
        self.form_widget.setLayout(self.form_layout)
        
        self.account_label = QLabel(str("账户"))
        self.account_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.pwd_label = QLabel(str("密码"))
        self.pwd_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.account_input = QLineEdit()
        self.account_input.setFixedHeight(25)
        self.pwd_input = QLineEdit()
        self.pwd_input.setFixedHeight(25)
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.form_layout.setContentsMargins(10, 10, 30, 10)
        self.form_layout.addWidget(self.account_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.account_input, 0, 1, 1, 3)
        self.form_layout.addWidget(self.pwd_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.pwd_input, 1, 1, 1, 3)

        # 登陆按钮部件
        self.btn_widget = QWidget()
        self.btn_widget.setObjectName("按钮区域")
        self.btn_layout = QGridLayout()
        self.btn_widget.setLayout(self.btn_layout)
        self.login_btn = QPushButton(str("登 陆"))
        self.registry_btn = QPushButton(str("注 册"))
        self.login_btn.clicked.connect(self.login)
        self.registry_btn.clicked.connect(self.registry)
        self.btn_layout.addWidget(self.login_btn, 0, 0, 1, 1)
        self.btn_layout.addWidget(self.registry_btn, 0, 1, 1, 1)
        self.login_btn.setFixedHeight(30)
        self.registry_btn.setFixedHeight(30)
        self.btn_layout.setSpacing(40)
        self.btn_layout.setContentsMargins(30, 0, 30, 0)

        # 标签部件      位置0行0列, 占位 1行4列
        self.main_layout.addWidget(self.label_widget, 0, 0, 1, 4)
        # 账号密码部件   位置1行0列, 占位 2行4列 
        self.main_layout.addWidget(self.form_widget, 1, 0, 2, 4)
        # 按钮部件      位置3行0列, 占位 1行4列
        self.main_layout.addWidget(self.btn_widget, 3, 0, 1, 4)

        self.login_status.connect(self.handle_login)
        self.login_msg.connect(self.message_box)
        self.setCentralWidget(self.main_widget)


    def login(self):
        usr = self.account_input.text()
        pwd = self.pwd_input.text()
        if not usr or not pwd:
            self.login_status.emit(LoginStatus.DO_NOT_EMPTY)
            return
        res = check_user(usr, pwd)
        if LoginStatus.SUCCEED == res:
            self.login_status.emit(LoginStatus.SUCCEED)
        else:
            self.login_status.emit(res)

    def registry(self):
        from .register import RegistryWindow

        self.registry_window = RegistryWindow()
        self.registry_window.show()
        self.close()

    def handle_login(self, msg):
        """
        process the signal emitted from button click event
        """
        if LoginStatus.SUCCEED == msg:
            from .main import MainWindow
            from crud.user import login_user
            login_user(self.account_input.text())
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            self.login_msg.emit(msg)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.login_btn.click()
