import requests
import json
import csv
from pprint import pprint

dataset_id = 653

# Я, к сожалению, не могу опубликовать на публичном ресуре свой личный api_key,
# так как буду использовать его в работе. Получить личный api_key можно после прохождения простой регистрации
# на https://apidata.mos.ru/Account/Login. Для подтверждения работы моего запроса, приложен скриншот.
api_key = 'ваш api_key'

main_link = f'https://apidata.mos.ru/v1/datasets/{dataset_id}/rows?$top=1&api_key={api_key}'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'}

response = requests.get(main_link,headers=header)

if response.ok:
    data = response.json()
    pprint(data)
    with open('result.json','wb') as f:
        f.write(response.content)

else:
    print(f' Сервер ответил:\n{response}')
