from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTimes
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

import twitter_spec

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

class Username(Base):
    __tablename__ = "usernames"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    username = Column(String(twitter_spec.max_username_length))

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    post_id = Column(Integer)
    post_date = Column(DateTime)
    media_id = Column(Integer)