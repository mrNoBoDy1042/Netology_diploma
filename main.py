# Необходимые библиотеки
import json
import requests
import time


# Описываем класс для работы и обработки данных VK API
class VkApi:
    # Необходимые начальные данные:
    #   CONFIG_FILE - путь к файлу с системныи параметрами (токен, версия API)
    #   TEST_USER_ID - имя тестовго пользователя (tim_leary)
    CONFIG_FILE = 'config.json'
    TEST_USER_ID = 'tim_leary'

    # Инициализируем класс и получаем токен и версию из config файла
    def __init__(self, config=CONFIG_FILE):
        # Читаем токен из config.json
        with open(config) as f:
            file = json.load(f)
        self.TOKEN, self.VERSION = file['token'], file['version']
        # Получаем id целевого пользователя
        self.USER_ID = input('Введите id целевого пользователя: ')
        # Если id пуст, то используем тестовый id
        if self.USER_ID == '':
            self.USER_ID = self.TEST_USER_ID

    # Получаем информацию целевого пользователя (номер id)
    def get_user_id(self):
        # Пробуем перевести переданный id пользователя в число для обращения к API
        try:
            self.USER_ID = int(self.USER_ID)
        # Если перевести не получается, то получаем номер от API VK
        except ValueError:
            # Параметры для запроса
            params = {
                'access_token': self.TOKEN,
                'user_ids': self.USER_ID,
                'fields': 'id',
                'v': self.VERSION
            }
            response = requests.get('https://api.vk.com/method/users.get', params)
            # Сохраняем полученный id как атрибут класса
            self.USER_ID = int(response.json()['response'][0]['id'])

    # Получаем список групп целевого пользователя
    def get_groups(self, user_id):
        if user_id == '':
            user_id = self.USER_ID
        # Параметры для запроса
        params = {
            'access_token': self.TOKEN,
            'user_id': user_id,
            'version': self.VERSION
        }
        response = requests.get('https://api.vk.com/method/groups.get', params)
        # Возвращаем множество групп пользователя
        try:
            return set(response.json()['response'])
        # Если возникла ошибка, то обрабатываем ее
        except KeyError:
            error_code = response.json()['error']['error_code']
            # Ошибка Too many requests per second
            if error_code == 6:
                # Делаем задержку
                time.sleep(1.5)
                # Повторяем запрос
                response = requests.get('https://api.vk.com/method/groups.get', params)
                return response.json()['response']
            # Ошибка Доступ запрещен, либо Пользователь был удален
            elif error_code in [7, 18]:
                # Возвращаем пустую строку
                return ''

    # Получаем список друзей целевого пользователя
    def get_friends(self):
        # Параметры для запроса
        params = {
            'access_token': self.TOKEN,
            'user_id': self.USER_ID,
            'version': self.VERSION
        }
        response = requests.get('https://api.vk.com/method/friends.get', params)
        return response.json()['response']

    # Собираем информацию о группах друзей и сверяем со своими группами
    def analyse_groups(self, friends):
        # Создаем множество общих групп
        common_groups = set()
        count = len(friends)

        # Проходим по каждому другу
        for friend in friends:
            print('Друзей осталось: ', count)
            count -= 1
            time.sleep(0.4)

            # Получаем список групп друга
            friends_group = self.get_groups(friend)
            # Если список групп получен, то анализируем его
            if friends_group:
                # Получаем общие группы
                common = user_groups & friends_group
                # Если они есть, то добавляем их в множество общих групп
                if common:
                    for group in common:
                        common_groups.add(group)

        # Возвращаем список уникальных групп целевого пользователя
        return list(user_groups - common_groups)

    # Получаем информацию о группах
    def get_group_info(self, groups_list):
        # Параметры для запроса
        params = {
            'access_token': self.TOKEN,
            'group_ids': str(groups_list).strip('[]'),
            'fields': 'members_count, name, id',
            'version': self.VERSION
        }
        response = requests.get('https://api.vk.com/method/groups.getById', params)
        return response.json()['response']

    # Нормализуем результаты
    def normalise_result(self, groups):
        result = []
        # Ключи ненужных данных
        keys = ['screen_name', 'is_closed', 'type', 'photo', 'photo_medium',  'photo_big']
        # Для каждой уникальной группы получаем информацию и убираем не нужные данные
        for group in groups:
            for key in keys:
                # Если ключа нет в списке нужных ключей, то удаляем поле
                if key in group.keys():
                    del group[key]
            # Сохраняем обработанные данные
            result.append(group)
        return result


# Создаем объект обработки данных
vk_api_controller = VkApi()

# Получаем id номер целевого пользователя
vk_api_controller.get_user_id()
friends_list = vk_api_controller.get_friends()
user_groups = vk_api_controller.get_groups('')

unique_groups = vk_api_controller.analyse_groups(friends_list)
groups_info = vk_api_controller.get_group_info(unique_groups)
result_info = vk_api_controller.normalise_result(groups_info)

with open('result.json', 'wb') as f:
    f.write(str(result_info).replace(', \'', ',\n\'').replace('}, ', '},\n').replace('\'', '"').encode('utf-8'))
