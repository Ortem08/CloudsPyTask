import json
import requests
import os


def get_all_folders(files):
    """Вывод всех папок на Диске"""
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


class YandexDisk:
    def __init__(self):
        """Инициализация класса YandexDisk
        Проверьте, что self.TOKEN соответствует имеено ВАШЕМУ токену"""

        self.URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.TOKEN = 'y0_AgAAAAAX419AAAnoxwAAAADjPIe21IqyXBZdS' \
                     'qGTURHTjFBpBZSUbFA'
        self.headers = {'Authorization': f'OAuth {self.TOKEN}'}

    def create_folder(self, path):
        """Создание папки.
        path: Путь к создаваемой папке на Диске"""

        params = {'path': path}
        requests.put(self.URL, headers=self.headers, params=params)

    def upload_file(self, path_source, path_result, replace=False):
        """Загрузка файла.
        path_result: Путь к файлу на Диске
        path_source: Путь к загружаемому файлу на компьютере
        replace: True или False - Замена файла на Диске при конфликте"""

        params = {
            'path': f'{path_result}{os.path.basename(path_source)}',
            'overwrite': replace
        }

        res = requests.get(f'{self.URL}/upload',
                           headers=self.headers, params=params).json()

        with open(path_source, 'rb') as f:
            try:
                requests.put(res['href'], files={'file': f})
            except KeyError:
                print(res)
                return
            print(f'File {os.path.basename(path_source)} '
                  f'uploaded successfully')

    def upload_folder(self, save_path, load_path):
        """Загрузка папки на Диск.
         save_path: Путь к папке на Диске
         load_path: Путь к загружаемой папке на компьютере"""

        date_folder = os.path.basename(load_path)

        for address, _, files in os.walk(load_path):
            try:
                folder_name = address.replace(load_path, "")[1:] \
                    .replace("\\", "/")
                self.create_folder(F'{save_path}/{date_folder}/{folder_name}')
                for file in files:
                    path_to_folder = address.replace(load_path, "") \
                        .replace("\\", "/")
                    self.upload_file(f'{address}/{file}',
                                     f'{save_path}/{date_folder}'
                                     f'{path_to_folder}/{file}', replace=True)
            except Exception:
                print('Can`t download')
                return
            print(f'Folder {os.path.basename(address)} uploaded successfully')

    def search(self, path):
        """Поиск файлов в указанной директории
         path: Путь к директории, в которой будет производится поиск"""

        params = {
            'fields': '_embedded.items.name, _embedded.items.path, '
                      '_embedded.items.type',
            'path': f'{path}'
        }
        res = requests.get(self.URL,
                           headers=self.headers, params=params).json()
        return res.get('_embedded').get('items')

    def get_file_info(self, name=None, is_folder=False):
        """Поиск информации о файле(-ах) с указанными именем
         name: Имя разыскиваемого файла или папки
         is_folder: Является ли разыскиваемый объект папкой?"""

        params = {'limit': '10000',
                  'fields': 'items.name,items.type,items.path'}
        res = requests.get(f'{self.URL}/files',
                           headers=self.headers, params=params).json()
        files = res.get('items')
        result = []

        if not is_folder and not name:
            result = files

        if is_folder:
            files = get_all_folders(files)

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

    def download_file(self, file, path=None):
        """Скачивание выбранного файла на компьютер
         file: json объект, описывающий желаемый файл
         path: Путь к загружаемому файлу"""
        if not path:
            path = 'Downloads'
        if not os.path.isdir(path):
            os.mkdir(path)

        request = requests.get(
            f'{self.URL}/download?path={file.get("path")}',
            headers=self.headers)
        download_url = request.json()['href']

        download_response = requests.get(download_url)
        with open(f'{path}/{file.get("name")}', 'wb') as f:
            f.write(download_response.content)

    def download_folder(self, folder, path=None):
        """Скачивание выбранной папки на компьютер
         folder: json объект, описывающий желаемую папку
         path: Путь к загружаемой папке"""
        if not path:
            path = f'Downloads/{folder.get("name")}'
        else:
            path = path + '/' + folder.get("name")
        if not os.path.isdir(path):
            os.mkdir(path)

        files = self.search(folder.get("path"))

        for file in files:
            if 'dir' in file.get("type"):
                self.download_folder(file, path)
            else:
                self.download_file(file, path)

        return True
