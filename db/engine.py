from sqlalchemy.engine import Engine, create_engine

from conf import settings


def _create_default_engine():
    # 所以这里传入的值为设置的dsn或者sqlite://（内存）
    dsn: str = settings.DATABASE
    if dsn.startswith("sqlite"):
        execution_options: dict = {
            "isolation_level": "SERIALIZABLE",
        }
    else:
        execution_options: dict = {
            "isolation_level": "READ COMMITTED",
        }

    engine: Engine = create_engine(
        dsn,
        pool_pre_ping=True,
        execution_options=execution_options,
        future=True,
    )

    return engine


default_engine = _create_default_engine
