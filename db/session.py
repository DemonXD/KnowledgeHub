import functools
import inspect
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker


def _create_default_sessionmaker() -> sessionmaker:
    from .engine import default_engine

    return sessionmaker(
        bind=default_engine(),
        future=True,
    )


DefaultSession: sessionmaker = _create_default_sessionmaker


@dataclass
class _DBStateInContext:
    session_args: dict
    session: Optional[Session] = None


_dbstate: ContextVar[Optional[_DBStateInContext]] = ContextVar("_dbstate", default=None)


class DBMeta(type):
    @property
    def session(self) -> Session:
        dbstate = _dbstate.get()
        if dbstate is None:
            raise RuntimeError("dbstate 未初始化。请在 `with DB():` 代码块中使用数据库。")

        if dbstate.session is None:
            dbstate.session = DefaultSession()(**dbstate.session_args)

        return dbstate.session


class DB(metaclass=DBMeta):
    def __init__(self, session_args: Optional[dict] = None):
        self.session_args: Optional[dict] = session_args or {}
        self.token: Optional[Token] = None

    def __enter__(self):
        self.token = _dbstate.set(_DBStateInContext(session_args=self.session_args))
        return type(self)

    def __exit__(self, exc_type, exc_value, traceback):
        dbstate = _dbstate.get()

        if dbstate.session is not None:
            """
            如果 session 为 None, 表示没有代码使用过数据库, 无需进行清理。
            """
            if exc_type is not None:
                dbstate.session.rollback()
            else:
                dbstate.session.commit()

        _dbstate.reset(self.token)
        self.token = None


def atomic(func):
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with DB.session.begin_nested():
                return await func(*args, **kwargs)

        return wrapper
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with DB():
                with DB.session.begin_nested():
                    return func(*args, **kwargs)
        return wrapper
