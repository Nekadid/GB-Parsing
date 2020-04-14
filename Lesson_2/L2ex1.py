from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import pandas as pd


def salary_check(salary_in):  # разбирает получаемый диапозон ЗП и отдает в виде словаря
    pat1 = r'^\d{1,10}(?=-)'
    pat2 = r'(?<=\s)\D{1,6}.*'
    pat3 = r'(?<=-)\d{1,10}(?=\s)'

    salary_in_mod = re.sub('(?<=\d)\s(?=\d)', '', salary_in)  # Убираем пробел

    if re.fullmatch(r'^\bдо.*', salary_in_mod):
        return {'top_salary': int(re.search(r'(?<=до\s).*(?=\s)', salary_in_mod)[0]), 'down_salary': 'None',
                'salary_value': re.search(pat2, salary_in_mod)[0]}
    else:
        if re.fullmatch(r'^\bот.*', salary_in_mod):
            return {'down_salary': int(re.search(r'(?<=от\s).*(?=\s)', salary_in_mod)[0]), 'top_salary': 'None',
                    'salary_value': re.search(pat2, salary_in_mod)[0]}
        else:
            if re.fullmatch(r'\b\d{1,}.*', salary_in_mod):
                return {'down_salary': int(re.search(pat1, salary_in_mod)[0]),
                        'top_salary': int(re.search(pat3, salary_in_mod)[0]),
                        'salary_value': re.search(pat2, salary_in_mod)[0]}
            else:
                return {'top_salary': 'None', 'down_salary': 'None', 'salary_value': 'None'}


vacancy_name = 'инженер'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
vacancies = []

# Начинаем парсить hh.ru
main_link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy_name}'
while True:

    html = requests.get(main_link, headers=header).text
    soup = bs(html, 'lxml')
    vacancy_blok = soup.find_all('div', {'class': 'vacancy-serp'})[0]
    vacancy_list = vacancy_blok.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancy_list:
        vacancy_link = vacancy.find('a')['href']
        vacancy_name = vacancy.find('a', {'class': 'bloko-link'}).getText()
        vacancy_salary = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()

        vacancy_data = {'name': vacancy_name,
                        'link': vacancy_link,
                        'down_salary': salary_check(vacancy_salary)['down_salary'],
                        'top_salary': salary_check(vacancy_salary)['top_salary'],
                        'website_origin': re.search(r'(?<=https://)\D{1,20}\.\D{1,3}(?=/)', main_link)[0],
                        'salary_value': salary_check(vacancy_salary)['salary_value']}
        vacancies.append(vacancy_data)
    try:
        link = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})['href']
        main_link = f'https://hh.ru{link}'
    except TypeError:
        break
pprint(vacancies)

df_vacancies = pd.DataFrame(vacancies)
print(df_vacancies)
