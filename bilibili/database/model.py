__all__ = ('session', 'User', 'Chat', 'Contribution', 'SignIn', 'Popularity', 'Follower')


import os

from sqlalchemy import (
    Column, Integer, String, Date, Time, Boolean,
    UniqueConstraint, ForeignKey, create_engine,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from ..conf import sqlite_path



engine = create_engine(f'sqlite:///{sqlite_path}')
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()

def __repr__(self):
    f = lambda x: not x.startswith('_')
    g = lambda k, v: f'{k}={repr(v)}'
    items = self.__dict__.items()
    return f'{self.__tablename__}({", ".join(g(k, v) for k, v in items if f(k))})'
Base.__repr__ = __repr__



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    sign_ins = relationship('SignIn', back_populates='user')
    chats = relationship('Chat', back_populates='user')
    contributions = relationship('Contribution', back_populates='user')


class Chat(Base):
    # 聊天记录
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    is_super = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='chats')


class Popularity(Base):
    __tablename__ = 'popularity'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    value = Column(Integer, nullable=False)


class Contribution(Base):
    __tablename__ = 'contribution'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    gift_name = Column(String, nullable=False)
    coin_type = Column(String, nullable=False)
    gift_number = Column(Integer, nullable=False)
    total_coin = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='contributions')


class SignIn(Base):
    # 签到
    __tablename__ = 'sign_in'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    UniqueConstraint('user_id', 'date')

    user = relationship('User', back_populates='sign_ins')


class Follower(Base):
    __tablename__ = 'follower'

    id = Column(Integer, primary_key=True)
    is_valid = Column(Boolean, nullable=False)
    date = Column(Date, nullable=False)  # 记录取关时间
    user_id = Column(Integer, ForeignKey('user.id'))


if not os.path.exists(sqlite_path):
    Base.metadata.create_all(engine, checkfirst=True)
