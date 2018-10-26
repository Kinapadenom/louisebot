import os
import sys
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property


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
    status = Column(Boolean, default=False)
    expenses = relationship("Expense", back_populates="user")
    presences = relationship("Presence", back_populates="user")

    @hybrid_property
    def balance(self):
        total = 0.0
        for expense in self.expenses:
            total += expense.amount
        for presence in self.presences:
            amount = presence.day.price
            total_amount = presence.meals * amount
            total -= total_amount
        return total

 
class Day(Base):
    __tablename__ = 'day'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=datetime.date.today())
    price = Column(Float, nullable=False, default=4.2)
    presences = relationship("Presence", back_populates="day")

class Expense(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User, back_populates="expenses")
    date = Column(Date, nullable=False, default=datetime.date.today())
    amount = Column(Float, nullable=False)
    description = Column(String(250))

class Presence(Base):
    __tablename__ = 'presence'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User, back_populates="presences")
    day_id = Column(Integer, ForeignKey('day.id'), nullable=False)
    day = relationship(Day, back_populates="presences")
    meals = Column(Integer, nullable=False, default=1)
    cook = Column(Integer, nullable=False, default=0)

 
# Create an engine that stores data
endpoint = config.get('default', 'endpoint')
db_host = config.get(endpoint, 'db_host')
db_name = config.get(endpoint, 'db_name')
db_user = config.get(endpoint, 'db_user')
db_pass = config.get(endpoint, 'db_pass')
engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_name))

DBSession = sessionmaker(bind=engine)
