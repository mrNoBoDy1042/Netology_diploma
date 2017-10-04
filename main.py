# Необходимые библиотеки
import requests
import json

# Локальные данные
VERSION = '5.67'
USER_ID = 'tim_leary'

# Читаем токен из config.json
# with open('config.json') as f:
#     token = json.load(f)['token']

token = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128'

# Параметры для запроса
params = {
    'access_token': token,
    'user_ids': USER_ID,
    'fields': 'id',
    'v': VERSION
}

# Получаем id номер страницы, если было передано имя пользователя
try:
    USER_ID = int(USER_ID)
except ValueError:
    response = requests.get('https://api.vk.com/method/users.get', params)
    USER_ID = int(response.json()['response'][0]['id'])

print(params)
print(response)

# Параметры для запроса
# params = {
#     'user_id': USER_ID,
#     'version': VERSION
# }
# print(params)
# response = requests.get('https://api.vk.com/method/friends.get', params)
# print(response)
# friends_list = response.json()
