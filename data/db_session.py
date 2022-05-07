import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    if db_file == 'b':
        conn_str = f'sqlite:///{"db/users.db".strip()}?check_same_thread=False'
        print(f"Подключение к базе данных по адресу {conn_str}")

        engine = sa.create_engine(conn_str, echo=False)
    else:
        conn_str = f'mysql+mysqldb://Paxnar:dud100dud@Paxnar.mysql.pythonanywhere-services.com/Paxnar$default'
        print(f"Подключение к базе данных по адресу {conn_str}")

        engine = sa.create_engine(conn_str, echo=False, pool_recycle=280)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
