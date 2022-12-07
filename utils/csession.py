from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class CustomDB:
    def __init__(self, dsn: str):
        self.session: Session = self._create_default_sessionmaker(dsn)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session is not None:
            self.session.close()

    def _create_default_sessionmaker(self, dsn: str) -> sessionmaker:
        engine = self._create_default_engine(dsn)
        return sessionmaker(bind=engine, future=True)()

    def _create_default_engine(self, dsn: str) -> Engine:
        # 所以这里传入的值为设置的dsn或者sqlite://（内存）
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
            echo=True,
            pool_pre_ping=True,
            execution_options=execution_options,
            future=True,
        )

        return engine
