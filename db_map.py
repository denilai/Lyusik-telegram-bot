from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class MediaIds(Base):
    __tablename__ = 'media_ids'
    id = Column(Integer, primary_key=True)
    file_id = Column(String(255))
    filename = Column(String(255))
    file_type = Column(String(255))
