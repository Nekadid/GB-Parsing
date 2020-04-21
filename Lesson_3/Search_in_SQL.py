from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import pandas as pd
import transliterate
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

engine = create_engine('mysql+pymysql://root:123@localhost:3306/new')

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(255))
    link = Column(String(255))
    website_origin = Column(String(255))
    down_salary = Column(Integer)
    top_salary = Column(Integer)
    salary_value = Column(String(255))

    def __init__(self, id, name, link, website_origin, down_salary, top_salary, salary_value):
        self.id = id
        self.name = name
        self.link = link
        self.website_origin = website_origin
        self.down_salary = down_salary
        self.top_salary = top_salary
        self.salary_value = salary_value

    def __repr__(self):
        return Vacancy(id=self.id , name=self.name, link=self.link, website_origin=self.website_origin, down_salary=self.down_salary,
                       top_salary=self.top_salary, salary_value=self.salary_value)


Session = sessionmaker(bind=engine)
session = Session()

# Вот это выводит имена и ссылки ваканчий с зп выше 80000
q = session.query(Vacancy)
DB = q.all()
for vacancy in DB:
    if isinstance(vacancy.top_salary, int):
        if vacancy.top_salary > 80000:
            print(vacancy.name, vacancy.link)

session.commit()
session.close()
