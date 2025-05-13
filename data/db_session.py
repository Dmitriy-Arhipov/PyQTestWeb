import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    """установка параметров соединения с БД"""
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import db_classes

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """текущее соединение с БД, тип объекта: Session"""
    global __factory
    return __factory()
