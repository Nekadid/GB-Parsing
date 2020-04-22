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
import json
import hashlib


def salary_check(salary_in):  # разбирает получаемый диапозон ЗП и отдает в виде словаря
    pat1 = r'^\d{1,10}(?=-)'
    pat2 = r'(?<=\s)\D{1,6}.*'
    pat3 = r'(?<=-)\d{1,10}(?=\s)'
    pat4 = r'^\d{1,10}(?=—)'
    pat5 = r'(?<=—)\d{1,10}(?=\s)'

    salary_in_mod = re.sub('(?<=\d)\s(?=\d)', '', salary_in)  # Убираем пробел для hh
    salary_in_mod = re.sub('(?<=—)\s(?=\d)', '', salary_in_mod)  # Убираем пробел sj
    salary_in_mod = re.sub('(?<=\d)\s(?=—)', '', salary_in_mod)  # Убираем пробел sj

    if re.fullmatch(r'^\bдо.*', salary_in_mod):
        return {'top_salary': int(re.search(r'(?<=до\s).*(?=\s)', salary_in_mod)[0]), 'down_salary': 0,
                'salary_value': re.search(pat2, salary_in_mod)[0]}
    else:
        if re.fullmatch(r'^\bот.*', salary_in_mod):
            return {'down_salary': int(re.search(r'(?<=от\s).*(?=\s)', salary_in_mod)[0]), 'top_salary': 0,
                    'salary_value': re.search(pat2, salary_in_mod)[0]}
        else:
            if re.fullmatch(r'\b\d{1,10}-\d{1,10}.*', salary_in_mod):
                return {'down_salary': int(re.search(pat1, salary_in_mod)[0]),
                        'top_salary': int(re.search(pat3, salary_in_mod)[0]),
                        'salary_value': re.search(pat2, salary_in_mod)[0]}
            else:
                if re.fullmatch(r'\b\d{1,10}—\d{1,10}.*', salary_in_mod):
                    return {'down_salary': int(re.search(pat4, salary_in_mod)[0]),
                            'top_salary': int(re.search(pat5, salary_in_mod)[0]),
                            'salary_value': re.search(pat2, salary_in_mod)[0]}
                else:
                    return {'top_salary': 0, 'down_salary': 0, 'salary_value': 0}

# Для ручного ввоода раскоментить след. 3 строки:
# vacancy_look_name = input('Введите название интресующей ваканисии на русском языке:')
# page_count_hh = int(input('Сколько первых страниц сайта www.hh.ru по вакансии просмотреть вывести результат:'))
# page_count_sj = int(input('Сколько первых страниц сайта www.superjob.ru по вакансии просмотреть вывести результат:'))

# Для ручного ввоода закоментить след. 3 строки:
vacancy_look_name = 'инженер'
page_count_hh = 1
page_count_sj = 0

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
vacancies = []

# Начинаем парсить https://www.superjob.ru/
vacancy_name_trans = transliterate.translit(vacancy_look_name, reversed=True)
main_link = f'https://russia.superjob.ru/vakansii/{vacancy_name_trans}.html'
i = 0
while i != page_count_sj:

    html = requests.get(main_link, headers=header).text
    soup = bs(html, 'lxml')
    vacancy_blok = soup.find('div', {'class': '_1ID8B'})
    vacancy_list = vacancy_blok.find_all('div',
                                         {'class': '_3zucV f-test-vacancy-item _3j3cA RwN9e _3tNK- _1NStQ _1I1pc'})

    for vacancy in vacancy_list:
        pre_vacancy_link = vacancy.find('a')['href']
        vacancy_link = f'https://russia.superjob.ru{pre_vacancy_link}'
        vacancy_name = vacancy.find('a').getText()
        vacancy_salary = vacancy.find('span', {
            'class': '_3mfro _2Wp8I _31tpt f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).getText()

        vacancy_data = {'name': vacancy_name,
                        'link': vacancy_link,
                        'website_origin': re.search(r'(?<=https://)\D{1,20}\.\D{1,3}(?=/)', main_link)[0],
                        'down_salary': salary_check(vacancy_salary)['down_salary'],
                        'top_salary': salary_check(vacancy_salary)['top_salary'],
                        'salary_value': salary_check(vacancy_salary)['salary_value']}
        vacancies.append(vacancy_data)
    try:
        link = soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'})['href']
        main_link = f'https://russia.superjob.ru{link}'
        i += 1
    except TypeError:
        break

# Начинаем парсить hh.ru
main_link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy_look_name}'
i = 0
while i != page_count_hh:

    html = requests.get(main_link, headers=header).text
    soup = bs(html, 'lxml')
    vacancy_blok = soup.find_all('div', {'class': 'vacancy-serp'})[0]
    vacancy_list = vacancy_blok.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancy_list:
        vacancy_link = vacancy.find('a')['href']
        id = hashlib.md5(vacancy_link.encode('utf-8'))
        vacancy_name = vacancy.find('a', {'class': 'bloko-link'}).getText()
        vacancy_salary = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()

        vacancy_data = {
                        'id': str(id.hexdigest()),
                        'name': vacancy_name,
                        'link': vacancy_link,
                        'website_origin': re.search(r'(?<=https://)\D{1,20}\.\D{1,3}(?=/)', main_link)[0],
                        'down_salary': salary_check(vacancy_salary)['down_salary'],
                        'top_salary': salary_check(vacancy_salary)['top_salary'],
                        'salary_value': salary_check(vacancy_salary)['salary_value']}
        vacancies.append(vacancy_data)
    try:
        link = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})['href']
        main_link = f'https://hh.ru{link}'
        i += 1
    except TypeError:
        break

# df_vacancies = pd.DataFrame(vacancies) # запись результатов парсинга в Датафрейм

# Раскоментить для выгрузки результатов парсинка в csv
# df_vacancies.to_csv('df_vacancies.csv', sep=';', encoding='utf-8')

engine = create_engine('mysql+pymysql://root:123@localhost:3306/new')

Base = declarative_base()
class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(String(255), primary_key=True, unique=True, autoincrement=False)
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
        return [self.id,
                self.name,
                self.link,
                self.website_origin,
                self.down_salary,
                self.top_salary,
                self.salary_value]

Session = sessionmaker(bind=engine)

# Base.metadata.create_all(engine) #Содание таблицы в БД



# Оформление результатов парсинга в виде списка (list_pars_vacancies) экземпляров класса Vacancy
list_pars_vacancies = []
for i in vacancies:
    s = Vacancy(i['id'],
                i['name'],
                i['link'],
                i['website_origin'],
                i['down_salary'],
                i['top_salary'],
                i['salary_value'])
    # print(i)
    list_pars_vacancies.append(s)

session = Session()
# session.add_all(list_pars_vacancies) Для первичной загрузки


for V_pars in list_pars_vacancies:
    BD_ans = session.query(Vacancy).filter_by(id = V_pars.id).first()
    if BD_ans is not None:
        if BD_ans.id == V_pars.id:
            if BD_ans.name != V_pars.name:
                BD_ans.name = V_pars.name
            if BD_ans.link != V_pars.link:
                BD_ans.link = V_pars.link
            if BD_ans.website_origin != V_pars.website_origin:
                BD_ans.website_origin = V_pars.website_origin
            if BD_ans.down_salary != V_pars.down_salary:
                BD_ans.down_salary = V_pars.down_salary
            if BD_ans.top_salary != V_pars.top_salary:
                BD_ans.top_salary = V_pars.top_salary
            if BD_ans.salary_value != V_pars.salary_value:
                BD_ans.salary_value = V_pars.salary_value
        else:
            continue
    else:
        session.add(V_pars)

# BD_ans = session.query(Vacancy).filter_by(id = V_pars.id).first()
# print(BD_ans.name)

# session.add_all(data)
session.commit()
session.close()
