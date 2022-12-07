from uuid import getnode

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox
)
from panels import BaseWindow, RegistryStatus
from crud.user import get_user, add_user


class RegistryWindow(BaseWindow):
    registry_status = pyqtSignal(str)
    registry_msg = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.mac = getnode()
        # self.setWindowOpacity(0.9)
        self.setFixedSize(400, 360)

        self.center()
        self.initUI()

        self.setWindowTitle('Registry')
        self.main_layout.setSpacing(0)

    def initUI(self):
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        # Registry 标签部件
        self.label_widget = QWidget()
        self.label_widget.setObjectName("Registry标签")
        self.label_layout = QGridLayout()
        self.label_widget.setLayout(self.label_layout)

        self.label = QLabel(str("Registry"))
        # set font
        label_font = self.label.font()
        label_font.setBold(True)
        label_font.setPointSize(26)
        self.label.setFont(label_font)
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
        self.confirm_label = QLabel(str("确认密码"))
        self.confirm_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.email_label = QLabel(str("邮箱"))
        self.email_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.account_input = QLineEdit()
        self.account_input.setFixedHeight(25)
        self.pwd_input = QLineEdit()
        self.pwd_input.setFixedHeight(25)
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_confirm_input = QLineEdit()
        self.pwd_confirm_input.setFixedHeight(25)
        self.pwd_confirm_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(25)
        self.form_layout.setContentsMargins(10, 10, 30, 10)
        self.form_layout.addWidget(self.account_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.account_input, 0, 1, 1, 3)
        self.form_layout.addWidget(self.pwd_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.pwd_input, 1, 1, 1, 3)
        self.form_layout.addWidget(self.confirm_label, 2, 0, 1, 1)
        self.form_layout.addWidget(self.pwd_confirm_input, 2, 1, 1, 3)
        self.form_layout.addWidget(self.email_label, 3, 0, 1, 1)
        self.form_layout.addWidget(self.email_input, 3, 1, 1, 3)

        # 登陆按钮部件
        self.btn_widget = QWidget()
        self.btn_widget.setObjectName("按钮区域")
        self.btn_layout = QGridLayout()
        self.btn_widget.setLayout(self.btn_layout)
        self.back_btn = QPushButton(str("返回"))
        self.registry_btn = QPushButton(str("确认"))
        self.back_btn.clicked.connect(self.back_to_login)
        self.registry_btn.clicked.connect(self.registry)
        self.btn_layout.addWidget(self.back_btn, 0, 0, 1, 1)
        self.btn_layout.addWidget(self.registry_btn, 0, 1, 1, 1)
        self.back_btn.setFixedHeight(30)
        self.registry_btn.setFixedHeight(30)
        self.btn_layout.setSpacing(40)
        self.btn_layout.setContentsMargins(30, 0, 30, 0)

        # 标签部件      位置0行0列, 占位 1行4列
        self.main_layout.addWidget(self.label_widget, 0, 0, 1, 4)
        # 账号密码部件   位置1行0列, 占位 3行4列 
        self.main_layout.addWidget(self.form_widget, 1, 0, 4, 4)
        # 按钮部件      位置4行0列, 占位 1行4列
        self.main_layout.addWidget(self.btn_widget, 5, 0, 1, 4)

        self.registry_status.connect(self.handle_registry)
        self.registry_msg.connect(self.message_box)
        self.setCentralWidget(self.main_widget)

    def back_to_login(self):
        from .login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def registry(self):
        name = self.account_input.text()
        pwd = self.pwd_input.text()
        pwd_confirm = self.pwd_confirm_input.text()
        email = self.email_input.text()

        if not pwd or not pwd_confirm:
            self.registry_status.emit(RegistryStatus.DO_NOT_EMPTY)
            return

        if pwd != pwd_confirm:
            self.registry_status.emit(RegistryStatus.CONFIRM_PASSWORD_NOT_CORRECT)
            return
        
        if email == "":
            self.registry_status.emit(RegistryStatus.EMAIL_EMPTY)
        
        user = get_user(name)
        if user is not None:
            self.registry_status.emit(RegistryStatus.USER_EXISTS)
            return
        
        user = add_user(name, pwd, email, self.mac)
        if user:
            self.registry_status.emit(RegistryStatus.SUCCEED)
            return
        else:
            self.registry_status.emit(RegistryStatus.FAILED)
            return

    def handle_registry(self, msg: str):
        if msg != RegistryStatus.SUCCEED:
            self.registry_msg.emit(msg)
        else:
            succeed_msg_box = QMessageBox()
            succeed_msg_box.setIcon(QMessageBox.Information)
            succeed_msg_box.setText("{} created successful".format(self.account_input.text()))
            succeed_msg_box.setWindowTitle("Congratulation!")
            succeed_msg_box.setStandardButtons(QMessageBox.Ok)
            rv = succeed_msg_box.exec()
            if rv == QMessageBox.Ok or rv == QMessageBox.Cancel:
                from .main import MainWindow
                from crud.user import login_user
                login_user(self.account_input.text())
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()               

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.registry_btn.click()
        elif event.key() == Qt.Key_Escape:
            self.back_btn.click()
