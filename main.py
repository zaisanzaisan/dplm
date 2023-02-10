import configparser
import json
import requests
from tqdm import tqdm
from time import sleep
from pprint import pprint
def access_token():
    access_token = input('Введите Ваш token api_vk: ')
    return access_token
def user_id():
    user_id = input('Введите идентификатор ВК пользователя : ')
    return user_id
def ya_token():
    ya_token = input('Введите token вашего Я.Диска: ')
    return ya_token
def write_config():
    config = configparser.ConfigParser()
    config['base info'] = {'access_token': access_token()}
    config['user info'] = {'user_id': user_id(),
                           'ya_token': ya_token()}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
def write_json(data):
    with open('photos.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
def get_largest(size_dict):
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    return size_dict['height']
def url_dict(url, name):
    photo_url = {'file name': name,
                 'url': url,
                 }
    for k, v in tqdm(photo_url.items(), ncols=80):
        sleep(0.25)
        pprint(photo_url)
        ya.upload_url(k, v)
class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_dir(self, dir_name=input('Введите название папки, куда добавятся фото: ')):
        headers = self.get_headers()
        params = {'path': f'disk:/{dir_name}'}
        url = "https://cloud-api.yandex.net/v1/disk/resources/"
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 404:
            params = {'path': f'disk:/{dir_name}'}
            requests.put(url, headers=headers, params=params)
        return dir_name

    def upload_url(self, filename, url_file):
        headers = self.get_headers()
        dir_name = self.get_dir()
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        filename = f'{dir_name}/{filename}'
        params = {'path': filename, 'url': url_file}
        response = requests.post(url=url, headers=headers, params=params)

        return response.json()
class VK:
    url = 'https://api.vk.com/method/'

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        users_get = self.url + 'users.get'
        params = {'user_ids': self.id}
        response = requests.get(users_get, params={**self.params, **params})
        res = response.json()
        closed_profile = [value['is_closed'] for k, v in tqdm(res.items(), ncols=80)  for value in v]
        if False in closed_profile:
            return self.photo_save()
        else:
            print(f'У данного пользователя закрытый профиль, скачивание файлов невозможно')

    def photo_save(self, count=5):
        photos_get = self.url + 'photos.get'
        params = {
            'owner_id': self.id,
            'album_id': 'profile',
            'extended': 1,
            'count': count,
            'photo_sizes': 1,
        }
        resp = requests.get(photos_get, params={**self.params, **params}).json()
        write_json(resp)
        photos = json.load(open('photos.json'))['response']['items']
        for photo in tqdm(photos, ncols=80):
            sleep(0.25)
            sizes = photo['sizes']
            max_size_url = max(sizes, key=get_largest)['url']
            name = str(photo['likes']['count']) + '_' + str(photo['date']) + '.jpg'
            url_dict(max_size_url, name)

if __name__ == '__main__':
    write_config()
    config = configparser.ConfigParser()
    config.read('config.ini')
    access_token = config['base info']['access_token']
    ya_token = config['user info']['ya_token']
    user_id = config['user info']['user_id']
    ya = YandexDisk(token=ya_token)
    vk = VK(access_token, user_id)
    pprint(vk.users_info())