import rsa
from cryptography.fernet import Fernet
from conf import config_settings


def encrypt_pwd(msg: str):
    fernet = Fernet(config_settings.SECRET.encode())
    encMsg = fernet.encrypt((msg).encode()).decode()
    return encMsg

def decrypt_pwd(pwd: str):
    fernet = Fernet(config_settings.SECRET.encode())
    decMsg = fernet.decrypt(pwd.encode()).decode()
    return decMsg

# only for test
def rsa_encryption(msg: str):
    pub_key, pri_key = rsa.newkeys(512)
    encMsg = rsa.encrypt(msg.encode(), pub_key)

    decMsg = rsa.decrypt(encMsg, pri_key).decode()
