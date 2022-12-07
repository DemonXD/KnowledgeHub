import nanoid
import string
from typing import Optional
from uuid import getnode

from utils.encryption import encrypt_pwd, decrypt_pwd
from db import DB, atomic
from schema import BookingUser
from crud import fetch_res_to_dict
from panels import LoginStatus


def login_user(name: str) -> None:
    from contexts import global_context
    user = get_user(name)
    if not user:
        raise Exception("user not found")
    global_context.user = user


def get_current_user() -> Optional[BookingUser]:
    from contexts import global_context
    if global_context.user is None:
        print("no login user found!, Something error, pls check")
        return
    return global_context.user


@atomic
def add_user(name: str, pwd: str, email: str, mac: str = getnode()) -> None:
        uid = nanoid.generate(string.ascii_letters+string.digits, 64)
        enc_pwd = encrypt_pwd(pwd)
        mac = mac

        if get_user(name) is not None:
            raise Exception("user:[%s] already exists" % name)

        user = BookingUser(name=name, uid=uid, mac=mac, email=email, password=enc_pwd)

        sql = """
        insert into BookingUser
        (uid, name, password, email, mac) 
        values
        ('{uid}','{name}','{password}','{email}','{mac}')
        """.format(**user.dict())
        try:
            DB.session.execute(sql)
            DB.session.commit()
        except Exception as e:
            print(str(e))
            DB.session.rollback()
            return
        else:
            return user

@atomic
def get_user(name: str) -> Optional[BookingUser]:
    sql = """
        select * from BookingUser
        where name='{}'
    """.format(name)

    cur = DB.session.execute(sql)
    res = cur.fetchone()
    if res is None:
        return
    
    user_dict = fetch_res_to_dict(res)
    user = BookingUser(**user_dict)
    return user

@atomic
def check_user(name: str, passwd: str) -> LoginStatus:
    user = get_user(name)
    if user is None:
        return LoginStatus.ACCOUNT_NOT_FOUND
    
    if passwd != decrypt_pwd(user.password):
        return LoginStatus.WRONG_PASSWORD
    
    return LoginStatus.SUCCEED


@atomic
def delete_user(name):
    user = get_user(name)
    if user is not None:
        try:
            DB.session.execute("delete from bookinguser where name='{}'".format(name))
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()
            return

@atomic
def modified_info(
    name: str, 
    old_password: str, 
    new_password: str, 
) -> bool:
    ...

