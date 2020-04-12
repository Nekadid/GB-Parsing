from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint


vacancy_name = 'инженер'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}
main_link = f'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text={vacancy_name}'
html = requests.get(main_link,headers=header).text
soup = bs(html,'lxml')

vacancy_blok = soup.find_all('div',{'class':'vacancy-serp'})[0]
vacancy_list = vacancy_blok.find_all('div',{'class':'vacancy-serp-item'})
#
vacancies = []
for vacancy in vacancy_list:
    vacancy_data = {}
    # pprint(vacancy)
    vacancy_link = vacancy.find('a')['href']
    vacancy_name = vacancy.find('a', {'class': 'bloko-link'}).getText()
    vacancy_salary = vacancy.find('div', {'class':'vacancy-serp-item__sidebar'}).getText()
    # break

    vacancy_data['name'] = vacancy_name
    vacancy_data['link'] = vacancy_link
    vacancy_data['salary'] = vacancy_salary
    vacancies.append(vacancy_data)


pprint(vacancies)
# # # pprint(vacancy_name)
pprint(vacancy)