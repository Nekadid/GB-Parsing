from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import pandas as pd
import transliterate


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
        return {'top_salary': int(re.search(r'(?<=до\s).*(?=\s)', salary_in_mod)[0]), 'down_salary': 'None',
                'salary_value': re.search(pat2, salary_in_mod)[0]}
    else:
        if re.fullmatch(r'^\bот.*', salary_in_mod):
            return {'down_salary': int(re.search(r'(?<=от\s).*(?=\s)', salary_in_mod)[0]), 'top_salary': 'None',
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
                    return {'top_salary': 'None', 'down_salary': 'None', 'salary_value': 'None'}


vacancy_name = input('Введите название интресующей ваканисии на русском языке:')
page_count_hh = int(input('Сколько первых вакансий с сайта www.hh.ru вывести результат:'))
page_count_sj = int(input('Сколько первых вакансий с сайта www.superjob.ru вывести результат:'))

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
vacancies = []

# Начинаем парсить https://www.superjob.ru/
vacancy_name_trans = transliterate.translit(vacancy_name, reversed=True)
main_link = f'https://russia.superjob.ru/vakansii/{vacancy_name_trans}.html'
i = 0
while i != page_count_sj:

    html = requests.get(main_link, headers=header).text
    # pprint(html)[0]
    soup = bs(html, 'lxml')
    vacancy_blok = soup.find('div', {'class': '_1ID8B'})
    # pprint(vacancy_blok)
    vacancy_list = vacancy_blok.find_all('div',
                                         {'class': '_3zucV f-test-vacancy-item _3j3cA RwN9e _3tNK- _1NStQ _1I1pc'})
    # pprint(vacancy_list)

    for vacancy in vacancy_list:
        pre_vacancy_link = vacancy.find('a')['href']
        vacancy_link = f'https://russia.superjob.ru{pre_vacancy_link}'
        vacancy_name = vacancy.find('a').getText()
        vacancy_salary = vacancy.find('span', {
            'class': '_3mfro _2Wp8I _31tpt f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).getText()

        vacancy_data = {'name': vacancy_name,
                        'link': vacancy_link,
                        'down_salary': salary_check(vacancy_salary)['down_salary'],
                        'top_salary': salary_check(vacancy_salary)['top_salary'],
                        'website_origin': re.search(r'(?<=https://)\D{1,20}\.\D{1,3}(?=/)', main_link)[0],
                        'salary_value': salary_check(vacancy_salary)['salary_value']}
        vacancies.append(vacancy_data)
    try:
        link = soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'})['href']
        main_link = f'https://russia.superjob.ru{link}'
        i += 1
    except TypeError:
        break

# Начинаем парсить hh.ru
main_link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy_name}'
i = 0
while i != page_count_hh:

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
        i += 1
    except TypeError:
        break

df_vacancies = pd.DataFrame(vacancies)
print(df_vacancies)
