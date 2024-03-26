from sqlalchemy import Column, DateTime, Integer, String
from urlc.database import Base


class ShortLink(Base):
    __tablename__ = "short_link"
    id = Column(Integer, primary_key=True)
    short_key = Column(String(30), unique=True, nullable=False)  # 短连接KEY，数据库唯一
    source_url = Column(String(300), nullable=False)  # 原连接
    created_time = Column(DateTime, nullable=False)

    def __init__(self, short_key=None, source_url=None, created_time=None):
        self.short_key = short_key
        self.source_url = source_url
        self.created_time = created_time

    def __repr__(self):
        return f"<short_link {self.source_url!r}>"
