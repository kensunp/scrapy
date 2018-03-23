#!/usr/bin/env python
# coding: utf-8
import pymysql

import datetime
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine,Column, Integer, String, Text,DateTime
from sqlalchemy.ext.declarative import declarative_base
from csdn.settings import DATABASE

pymysql.install_as_MySQLdb()
Base = declarative_base()
metadata = Base.metadata

def db_connect():
    return create_engine(URL(**DATABASE))

def create_blog_table(engine):
    Base.metadata.create_all(engine)

def _get_date():
    return datetime.datatime.now()

class Article(Base):
    """文章类"""
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(100))
    title = Column(String(100))
