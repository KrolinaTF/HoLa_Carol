from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from typing import Optional
from src.utils.config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    queries = relationship("Query", back_populates="user")

class Query(Base):
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    query_text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="queries")
    results = relationship("QueryResult", back_populates="query")

class QueryResult(Base):
    __tablename__ = 'query_results'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('queries.id'))
    response = Column(String)
    confidence = Column(Float)
    domain = Column(String)
    query = relationship("Query", back_populates="results")

def init_db(database_url: Optional[str] = None):
    engine = create_engine(database_url or settings.DATABASE_URL, echo=settings.DEBUG)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()