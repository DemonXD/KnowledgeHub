from PyQt5.QtCore import pyqtSignal, QObject

from typing import Optional
from schema.user import BookingUser


class ContextManager(QObject):
    global_signal: pyqtSignal = pyqtSignal(str)
    user: Optional[BookingUser] = None


global_context = ContextManager()

__all__ = ["global_context"]