import json


import requests
import os


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
    params = {
        'path': f'{path_result}{os.path.basename(path_source)}',
        'overwrite': replace
    }

    res = requests.get(f'{URL}/upload',
                       headers=headers, params=params).json()

    with open(path_source, 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)
            return
        print(f'File {os.path.basename(path_source)} uploaded successfully')


def upload_folder(savepath, loadpath):
    """Загрузка папки на Диск.
     savepath: Путь к папке на Диске
     loadpath: Путь к загружаемой папке на компе"""

    date_folder = os.path.basename(loadpath)

    for address, _, files in os.walk(loadpath):
        try:
            folder_name = address.replace(loadpath, "")[1:].replace("\\", "/")
            create_folder(F'{savepath}/{date_folder}/{folder_name}')
            for file in files:
                path_to_folder = address.replace(loadpath, "").replace("\\", "/")
                upload_file(f'{address}/{file}',
                            f'{savepath}/{date_folder}{path_to_folder}/{file}', replace=True)
        except Exception:
            print('Can`t download')
            return
        print(f'Folder {os.path.basename(address)} uploaded successfully')


def search(path):
    params = {
        'fields': '_embedded.items.name, _embedded.items.path, _embedded.items.type',
        'path': f'{path}'
    }
    response = requests.get('https://cloud-api.yandex.net/v1/disk/resources',
                            headers=headers, params=params).json()

    return response.get('_embedded').get('items')


def get_file_info(name=None, is_folder=False):
    params = {'limit': '10000',
              'fields': 'items.name,items.type,items.path'}
    response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/files',
                            headers=headers, params=params).json()
    files = response.get('items')
    result = []

    if not is_folder and not name:
        result = files

    if is_folder:
        files = get_all_folders(files=files)

    if name and not is_folder:
        for file in files:
            if file.get('name') == name:
                result.append(file)
    elif name and is_folder:
        for file in files:
            decoded = json.loads(file)
            if decoded.get('name') == name:
                result.append(decoded)

    if len(result) > 1:
        for file in result:
            if 'dir' in file.get("type"):
                print(
                    F'{file.get("name")}, путь: {file.get("path")}, Папка')
            else:
                print(
                    F'{file.get("name")}, путь: {file.get("path")}, Файл')

    return result


def get_all_folders(files):
    folders = set()
    for file in files:
        full_path = file.get('path')
        folder_name = full_path.split('/')[-2]
        folder_path = full_path[
                      :full_path.rfind(folder_name) + len(folder_name)]
        if folder_name != 'disk:':
            folder = {'name': folder_name, 'path': folder_path, 'type': 'dir'}
            folders.add(json.dumps(folder))

    return folders


def download_file(file, path=None):
    if not path:
        path = 'Downloads'
    if not os.path.isdir(path):
        os.mkdir(path)

    request = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources/download?path={file.get("path")}', headers=headers)
    download_url = request.json()['href']

    download_response = requests.get(download_url)
    with open(f'{path}/{file.get("name")}', 'wb') as f:
        f.write(download_response.content)


def download_folder(folder, path=None):
    if not path:
        path = f'Downloads/{folder.get("name")}'
    else:
        path = path + '/' + folder.get("name")
    if not os.path.isdir(path):
        os.mkdir(path)

    files = search(folder.get("path"))

    for file in files:
        if 'dir' in file.get("type"):
            download_folder(file, path)
        else:
            download_file(file, path)

    return True
