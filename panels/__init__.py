from enum import Enum
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QMainWindow, QDesktopWidget, QMessageBox,
    QFrame, QSizePolicy, QTabWidget, QWidget,
    QGridLayout, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import QObject, QEvent
from contexts import global_context


class LoginStatus(str, Enum):
    SUCCEED             = "SUCCEED"
    FAILED              = "FAILED"
    DO_NOT_EMPTY        = "Do Not Empty"
    WRONG_PASSWORD      = "Wrong Password"
    ACCOUNT_NOT_FOUND   = "Not Found Account"


class RegistryStatus(str, Enum):
    SUCCEED                         = "SUCCEED"
    FAILED                          = "FAILED"
    DO_NOT_EMPTY                    = "Do Not Empty"
    CONFIRM_PASSWORD_NOT_CORRECT    = "Confirm password not correct"
    USER_EXISTS                     = "BookingUser already exists"
    EMAIL_EMPTY                     = "请输入邮箱, 用户充值密码"


class ConfigStatus(str, Enum):
    SWITCH_TO_LOGIN = "switch to login window"


class GlobalEventFilter(QObject):
    """
    usage:
        in any window:
            ins = GlobalEventFilter()
            self.installEventFilter(ins)
    """
    def eventFilter(self, obj: QObject, evt: QEvent) -> bool:
        print("worked") 
        return super(GlobalEventFilter, self).eventFilter(obj, evt)


class CustomTabWidget(QTabWidget):
    in_tab = None
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabBar().installEventFilter(self)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        print(obj.objectName(), event.__str__())
        return super().eventFilter(obj, event)


class BaseWindow(QMainWindow):
    context = global_context
    def __init__(self):
        super().__init__()
        self.context.global_signal.connect(self.message_box)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
    
    def message_box(self, msg: str):
        """
        popup warning message box
        """
        QMessageBox.warning(self, "WARNING", msg, QMessageBox.Yes)

    def gen_font(self, pointSize: int) -> QtGui.QFont:
        return QtGui.QFont("Sarasa Mono SC", pointSize)
    
    def get_line_sep(self, width: int = 1) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sep.setLineWidth(width)
        return sep


class CGridLayoutWidget(QWidget):
    def __init__(self, no_spacing=True, no_content_margin=True, *args, **kwargs):
        super(CGridLayoutWidget, self).__init__(*args, **kwargs)
        self.main_layout = QGridLayout()
        if no_spacing:
            self.main_layout.setSpacing(0)
        if no_content_margin:
            self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)


class CHBoxLayoutWidget(QWidget):
    def __init__(self, no_spacing=True, no_content_margin=True, *args, **kwargs):
        super(CHBoxLayoutWidget, self).__init__(*args, **kwargs)
        self.main_layout = QHBoxLayout()
        if no_spacing:
            self.main_layout.setSpacing(0)
        if no_content_margin:
            self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)


class CVBoxLayoutWidget(QWidget):
    def __init__(self, no_spacing=True, no_content_margin=True, *args, **kwargs):
        super(CVBoxLayoutWidget, self).__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout()
        if no_spacing:
            self.main_layout.setSpacing(0)
        if no_content_margin:
            self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
       
