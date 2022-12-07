import os
import yaml
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton
)

from panels import BaseWindow, ConfigStatus
from utils.common import dump_dict_to_yaml_file


class ConfigWindow(BaseWindow):
    config_status = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.config_status.connect(self.handle_config)

        # self.setWindowOpacity(0.9)
        self.setFixedSize(400, 500)

        self.center()
        self.initUI()

        self.setWindowTitle('Initial')
        # self.resize(320, 240)
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint)

    def initUI(self):
        
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setSpacing(0)

        self.db_widget = QWidget()
        self.db_layout = QGridLayout()
        self.db_widget.setLayout(self.db_layout)

        self.db_dsn_label = QLabel()
        self.db_dsn_label.setText("数据库: 例(本地sqlite), sqlite:///app.db")
        self.db_dsn_label.setAlignment(Qt.AlignLeft)
        self.db_dsn_input = QLineEdit()
        self.db_dsn_input.setFixedHeight(25)
        self.db_layout.addWidget(self.db_dsn_label, 0, 0, 1, 4)
        self.db_layout.addWidget(self.db_dsn_input, 1, 0, 1, 4)
        

        self.email_widget = QWidget()
        self.email_layout = QGridLayout()
        self.email_widget.setLayout(self.email_layout)

        self.email_host_label = QLabel()
        self.email_host_label.setText("smtp服务器: 例, smtp.163.com")
        self.email_host_label.setAlignment(Qt.AlignLeft)
        self.email_host_input = QLineEdit()
        self.email_host_input.setFixedHeight(25)

        self.email_port_label = QLabel()
        self.email_port_label.setText("smtp端口: 例, 25")
        self.email_port_label.setAlignment(Qt.AlignLeft)
        self.email_port_input = QLineEdit()
        self.email_port_input.setFixedHeight(25)

        self.email_sender_label = QLabel()
        self.email_sender_label.setText("smtp授权账户: 例, xxx@163.com")
        self.email_sender_label.setAlignment(Qt.AlignLeft)
        self.email_sender_input = QLineEdit()
        self.email_sender_input.setFixedHeight(25)

        self.email_token_label = QLabel()
        self.email_token_label.setText("授权码: 邮箱配置smtp服务的授权码")
        self.email_token_label.setAlignment(Qt.AlignLeft)
        self.email_token_input = QLineEdit()
        self.email_token_input.setFixedHeight(25)
        
        self.email_test_label = QLabel(str("测试邮件: 测试上述配置项是否正确"))
        self.email_test_label.setAlignment(Qt.AlignLeft)
        self.email_test_input = QLineEdit()
        self.email_test_input.setFixedHeight(25)
        self.email_test_button = QPushButton("发送")
        self.email_test_button.setFixedWidth(50)
        self.email_test_button.setFixedHeight(25)

        self.email_layout.addWidget(self.email_host_label, 0, 0, 1, 4)
        self.email_layout.addWidget(self.email_host_input, 1, 0, 1, 4)
        self.email_layout.addWidget(self.email_sender_label, 2, 0, 1, 4)
        self.email_layout.addWidget(self.email_sender_input, 3, 0, 1, 4)
        self.email_layout.addWidget(self.email_port_label, 4, 0, 1, 4)
        self.email_layout.addWidget(self.email_port_input, 5 ,0, 1, 4)
        self.email_layout.addWidget(self.email_token_label, 6, 0, 1, 4)
        self.email_layout.addWidget(self.email_token_input, 7, 0, 1, 4)
        self.email_layout.addWidget(self.email_test_label, 8, 0, 1, 4)
        self.email_layout.addWidget(self.email_test_input, 9, 0, 1, 3)
        self.email_layout.addWidget(self.email_test_button, 9, 3, 1, 1)
        self.email_test_button.clicked.connect(self.check_email_config)


        self.confirm_button_widget = QWidget()
        self.confirm_button_layout = QVBoxLayout()
        self.confirm_button_widget.setLayout(self.confirm_button_layout)
        self.confirm_button = QPushButton(str("确 认"))
        self.confirm_button.setFixedWidth(70)
        self.confirm_button.setFixedHeight(30)
        self.confirm_button_layout.addWidget(self.confirm_button)
        self.confirm_button_layout.setSpacing(0)
        self.confirm_button_layout.setAlignment(Qt.AlignCenter)
        self.confirm_button.clicked.connect(self.set_config)
        

        self.main_layout.addWidget(self.db_widget, 0, 0, 2, 4)
        self.main_layout.addWidget(self.email_widget, 2, 0, 10, 4)
        self.main_layout.addWidget(self.confirm_button_widget, 12, 0, 1, 4)

        self.setCentralWidget(self.main_widget)

    def handle_config(self, msg: str):
        # 跳转loginWindow
        if ConfigStatus.SWITCH_TO_LOGIN == msg:
            from panels.index.login import LoginWindow
            login_win = LoginWindow()
            login_win.show()
            self.close()

    def check_email_config(self):
        email_host = self.email_host_input.text()
        email_sender = self.email_sender_input.text()
        email_port = self.email_port_input.text()
        email_token = self.email_token_input.text()
        email_receiver = self.email_test_input.text()
        if email_host != "" and email_port != "" and \
            email_sender != "" and email_token != "" and email_receiver != "":
            from utils.email import Emailer
            try:
                client = Emailer(email_host, email_sender, int(email_port), email_token)
                client.email(receivers=email_receiver, message="Test for test button", subject="Test")
            except Exception as e:
                self.message_box(str(e))
        else:
            self.message_box("缺少配置项, 请检查email相关配置是否齐全")


    def set_config(self):
        res = {"booking": None}
        dsn = self.db_dsn_input.text()
        email_host = self.email_host_input.text()
        email_sender = self.email_sender_input.text()
        email_port = self.email_port_input.text()
        email_token = self.email_token_input.text()

        if not dsn:
            dsn = "sqlite:///app.db"

        res["booking"] = {"DATABASE": dsn}

        try:
            from commands.initdb import init_table
            if email_host != "" and email_port != "" and \
                email_sender != "" and email_token != "":
                res["booking"].update({
                    "EMAIL_CONFIG": {
                        "SERVER": email_host,
                        "SENDER": email_sender,
                        "PORT": int(email_port),
                        "TOKEN": email_token
                    }
                })
            dump_dict_to_yaml_file("config.yaml", res)
            init_table(dsn)
            with open("./global.config.yaml", "r") as f:
                data = yaml.safe_load(f)
            with open("./global.config.yaml", "w") as f:
                data["global"]["IS_INITIAL"] = True
                yaml.dump(data, f)
        except Exception as e:
            print(str(e))
            if Path("./config.yaml").exists:
                os.remove("./config.yaml")
        else:
            # import importlib
            # import conf
            # importlib.reload(conf)
            # self.config_status.emit(ConfigStatus.SWITCH_TO_LOGIN)
            self.message_box("初始化成功, 请再次运行程序!")
            self.close()

    # def refresh(self):
    #     main_win = BaseWindow()
    #     config_win = ConfigWindow()
    #     config_win.initUI(main_win)
    #     main_win.repaint()
