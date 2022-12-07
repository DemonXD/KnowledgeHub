import smtplib
from typing import Optional, Union, List

from email.mime.text import MIMEText
from email.header import Header

# config 界面调用这里的Emailer会报错settings配置文件找不到，这里不用理会
from conf import settings 


class ImproperlyConfigured(Exception):
    """
    用于所有跟配置错误相关的场景
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__()

    def __str__(self):
        return self.message


class Emailer:
    def __init__(
        self,
        server: Optional[str] = settings.EMAIL_CONFIG.SERVER or None,
        sender: Optional[str] = settings.EMAIL_CONFIG.SENDER or None,
        port: Optional[int] = settings.EMAIL_CONFIG.PORT or None,
        token: Optional[str] = settings.EMAIL_CONFIG.TOKEN or None,
    ):
        if server is None or sender is None or \
            port is None or token is None:
           raise ImproperlyConfigured("Email config 缺少配置项")
        self.sender = sender
        self.server = server
        self.port = 25
        self.token = token
        self.client = smtplib.SMTP()
        self.init_client()

    def init_client(self):
        try:
            self.client.connect(self.server, self.port)
            self.client.login(self.sender, self.token)
        except Exception as e:
            print(str(e))
            raise e

    def __enter__(self):
        return self

    def email(
        self,
        receivers: Union[str, List[str]],
        message: str,
        subject: str,
        _from: str = "Knowledge Hub",
    ) -> None:
        try:
            message = MIMEText(message, 'plain', 'utf-8')
            message["From"] = Header(_from, "utf-8")
            message['Subject'] = Header(subject, "utf-8")
            self.client.sendmail(self.sender, receivers, message.as_string())
        except Exception as e:
            print(str(e))

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            print(str(exc_value))
        self.client.close()

    def __del__(self):
        self.client.close()