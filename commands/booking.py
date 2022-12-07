import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from panels.index.config import ConfigWindow
from panels.index.login import LoginWindow
from conf import config_settings


def command():
    try:
        if not Path("./global.config.yaml").exists():
            raise Exception("ATTENTION: global.config.yaml not exists!")

        app = QApplication(sys.argv)
        app.setFont(QFont("Sarasa Mono SC"))
        if config_settings.IS_INITIAL and Path("./config.yaml").exists():
            window = LoginWindow()
        else:
            window = ConfigWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(str(e))
        pass
