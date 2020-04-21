from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:123@localhost:3306/new')
Base = declarative_base()
print(Base)
print(engine.table_names())


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


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
print(engine.table_names())

session.commit()
session.close()
