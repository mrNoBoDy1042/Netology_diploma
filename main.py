# Необходимые библиотеки
import requests, json, time, pprint

# Локальные данные
USER_ID = 'tim_leary'
CONFIG_FILE = 'config.json'


def init(config):
    # Читаем токен из config.json
    with open(config) as f:
        file = json.load(f)
    return file['token'], file['version']


def get_user_id(user_name, token, version):
    # Параметры для запроса
    params = {
        'access_token': token,
        'user_ids': user_name,
        'fields': 'id',
        'v': version
    }
    # Получаем id номер страницы, если было передано имя пользователя
    try:
        user_id = int(user_name)
    except ValueError:
        response = requests.get('https://api.vk.com/method/users.get', params)
        user_id = int(response.json()['response'][0]['id'])
    return user_id


def get_groups(user_id, token, version):
    # Параметры для запроса
    params = {
        'access_token': token,
        'user_id': user_id,
        'version': version
    }
    response = requests.get('https://api.vk.com/method/groups.get', params)
    try:
        return set(response.json()['response'])
    except KeyError:
        error_code = response.json()['error']['error_code']
        if error_code == 6:
            time.sleep(1.5)
            response = requests.get('https://api.vk.com/method/groups.get', params)
            return response.json()['response']
        elif error_code in [7, 18]:
            return ''


def get_friends(user_id, token, version):
    # Параметры для запроса
    params = {
        'access_token': token,
        'user_id': user_id,
        'version': version
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    return response.json()['response']


TOKEN, VERSION = init(CONFIG_FILE)
USER_ID = get_user_id(USER_ID, TOKEN, VERSION)
friends_list = get_friends(USER_ID, TOKEN, VERSION)
groups_set = get_groups(USER_ID, TOKEN, VERSION)


friends_groups = {}
count = len(friends_list)
for friend in friends_list:
    print('Друзей осталось: ', count)
    count -= 1
    time.sleep(0.3)
    friends_groups[friend] = get_groups(friend, TOKEN, VERSION)

pprint.pprint(friends_groups)
