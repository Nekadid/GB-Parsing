import requests
from pprint import pprint

login = input('Введите логин пользователя для поиска публичных репозиториев: ')

# Сторочка для проверки со статичным логином
# login = 'nekadid'

main_link = f'https://api.github.com/users/{login}/repos'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}

response = requests.get(main_link,headers=header)

# Раскоментить чтобы посмотреть ответ сервера
# pprint(response.text)

if response.ok:
    data = response.json()
    print(f'У пользователя с ником {data[0]["owner"]["login"]} имеются следующие публичные репозитории:')
    for i in data:

        print(i['name'])
else:
    print(f' Сервер ответил:\n{response.text}')