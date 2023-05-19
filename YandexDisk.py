import re

import requests
import os
from datetime import datetime


URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAAAAAcmCfkAAnoxwAAAADjPGamE13EKlY-TvW1eh6xotNaz58030o'
headers = {'Authorization': f'OAuth {TOKEN}'}


def create_folder(path):
    """Создание папки.
    path: Путь к создаваемой папке на Диске"""

    params = {'path': path}
    requests.put(URL, headers=headers, params=params)


def upload_file(path_source, path_result, replace=False):
    """Загрузка файла.
    path_result: Путь к файлу на Диске
    path_source: Путь к загружаемому файлу на компе
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={path_result}&overwrite={replace}',
                       headers=headers).json()

    with open(path_source, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)


def upload_folder(savepath, loadpath):
    """Загрузка папки на Диск.
     savepath: Путь к папке на Диске
     loadpath: Путь к загружаемой папке на компе"""

    date_folder = '{0}_{1}'.format(loadpath.split('\\')[-1], datetime.now().strftime("%Y"))
    create_folder(savepath)
    for address, _, files in os.walk(loadpath):
        create_folder('{0}/{1}/{2}'.format(savepath, date_folder, address.replace(loadpath, "")[1:].replace("\\", "/")))
        for file in files:
            upload_file('{0}\{1}'.format(address, file),
                        '{0}/{1}{2}/{3}'.format(savepath, date_folder, address.replace(loadpath, "").replace("\\", "/"), file), replace=True)


def search(path):
    params = {
        'fields': '_embedded.items.name, _embedded.items.path, _embedded.items.type',
        'path': f'{path}'
    }
    response = requests.get('https://cloud-api.yandex.net/v1/disk/resources',
                            headers=headers, params=params).json()

    return response.get('_embedded').get('items')


def get_all_files(is_folder=False):
    params = {'limit': '10000',
              'fields': 'items.name,items.type,items.path'}
    response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/files',
                            headers=headers, params=params).json()
    files = response.get('items')

    if is_folder:
        folders = set()
        for file in files:
            full_path = file.get('path')
            folder_name = full_path.split('/')[-2]
            folder_path = full_path[:full_path.rfind(folder_name)+len(folder_name)]
            if folder_name != 'disk:':
                folders.add((folder_name, folder_path))
        return folders

    return files


def main():
    get_all_files(True)


if __name__ == '__main__':
    main()
