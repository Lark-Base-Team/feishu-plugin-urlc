from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database/urlc.db")

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
    # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
    import urlc.models

    Base.metadata.create_all(bind=engine)
