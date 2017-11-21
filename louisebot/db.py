import os
import sys
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


from .config import config
 
Base = declarative_base()
 
class User(Base):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    slackid = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    admin = Column(Boolean, default=False)
 
class Day(Base):
    __tablename__ = 'day'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=datetime.date.today())
    price = Column(Float, nullable=False, default=5.0)

class Expense(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    day = Column(Date, nullable=False, default=datetime.date.today())
    amount = Column(Float, nullable=False)
    description = Column(String(250))

class Presence(Base):
    __tablename__ = 'presence'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    day_id = Column(Integer, ForeignKey('day.id'), nullable=False)
    day = relationship(User)
    meals = Column(Integer, nullable=False, default=1)


 
# Create an engine that stores data
endpoint = config.get('default', 'endpoint')
db_host = config.get(endpoint, 'db_host')
db_name = config.get(endpoint, 'db_name')
db_user = config.get(endpoint, 'db_user')
db_pass = config.get(endpoint, 'db_pass')
engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_name))

DBSession = sessionmaker(bind=engine)
