from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re


def salary_check(salary_in):
    pat1 = r'^\d{1,6}\s\d{1,6}(?=\D)'
    pat2 = r'\s\D{1,6}.*'
    pat3 = r'(?<=-)\d{1,6}\s\d{1,6}(?=\s)'

    salary_in_mod = re.sub('\xa0', ' ', salary_in)  # Преобразуем \xa0 в обычный пробел

    if re.fullmatch(r'^\bдо.*', salary_in_mod):
        return {'top_salary': salary_in_mod, 'down_salary': 'None'}
    else:
        if re.fullmatch(r'^\bот.*', salary_in_mod):
            return {'down_salary': salary_in_mod, 'top_salary': 'None'}
        else:
            if re.fullmatch(r'\b\d{1,}.*', salary_in_mod):
                return {'down_salary': f'{re.search(pat1, salary_in_mod)[0]}{re.search(pat2, salary_in_mod)[0]}',
                        'top_salary': f'{re.search(pat3, salary_in_mod)[0]}{re.search(pat2, salary_in_mod)[0]}'}
            else:
                return {'top_salary': 'None', 'down_salary': 'None'}


vacancy_name = 'инженер'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
main_link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy_name}'

vacancies = []
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
                        'website_origin': re.search(r'(?<=https://)\D{1,20}\.\D{1,3}(?=/)', main_link)[0]}
        vacancies.append(vacancy_data)
    try:
        link = soup.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})['href']
        main_link = f'https://hh.ru{link}'
    except TypeError:
        break
pprint(vacancies)

