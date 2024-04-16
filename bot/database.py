from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot.config import DATABASE_CONNECTION_STRING

Base = declarative_base()


class TaskModel(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    deadline = Column(DateTime)
    description = Column(String)
    project = Column(String)


engine = create_engine(DATABASE_CONNECTION_STRING)

Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()
