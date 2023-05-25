import json
import requests
import os

from requests.exceptions import HTTPError


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
        Проверьте, что self.TOKEN соответствует именно ВАШЕМУ токену
        """
        self.URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.TOKEN = 'y0_AgAAAAAcmCfkAAnoxwAAAADjPGamE13EKlY' \
                     '-TvW1eh6xotNaz58030o '
        self.headers = {'Authorization': f'OAuth {self.TOKEN}'}

    def create_folder(self, path):
        """Создание папки.
        Args:
            path: Путь к создаваемой папке на Диске
        """
        params = {'path': path}
        try:
            requests.put(self.URL, headers=self.headers, params=params)
        except requests.exceptions.RequestException:
            raise HTTPError

    def upload_file(self, path_source, path_result, replace=False):
        """Загрузка файла.
        Args:
            path_result: Путь к файлу на Диске
            path_source: Путь к загружаемому файлу на компьютере
            replace: True/False - Замена файла на Диске при конфликте
        Returns: True если успех
        """
        params = {
            'path': f'{path_result}{os.path.basename(path_source)}',
            'overwrite': replace
        }

        try:
            res = requests.get(f'{self.URL}/upload',
                               headers=self.headers, params=params).json()
            with open(path_source, 'rb') as f:
                requests.put(res['href'], files={'file': f})
        except requests.exceptions.RequestException:
            return HTTPError

        print(f'File {os.path.basename(path_source)} '
              f'uploaded successfully')
        return True

    def upload_folder(self, save_path, load_path):
        """Загрузка папки на Диск.
        Args:
            save_path: Путь к папке на Диске
            load_path: Путь к загружаемой папке на компьютере
        Returns: True если успех
        """

        date_folder = os.path.basename(load_path)
        try:
            for address, _, files in os.walk(load_path):
                folder_name = address.replace(load_path, "")[1:] \
                    .replace("\\", "/")
                self.create_folder(F'{save_path}/{date_folder}/{folder_name}')
                for file in files:
                    path_to_folder = address.replace(load_path, "") \
                        .replace("\\", "/")
                    self.upload_file(f'{address}/{file}',
                                     f'{save_path}/{date_folder}'
                                     f'{path_to_folder}/{file}',
                                     replace=True)
                print(
                    f'Folder {os.path.basename(address)} uploaded successfully'
                )
        except requests.exceptions.RequestException:
            print('Can`t upload')
            raise HTTPError

        return True

    def search(self, path):
        """Поиск файлов в указанной директории
        Args:
            path: Путь к директории, в которой будет производиться поиск
        Returns: Лист файлов в данной папке
        """

        params = {
            'fields': '_embedded.items.name, _embedded.items.path, '
                      '_embedded.items.type',
            'path': f'{path}'
        }
        try:
            res = requests.get(self.URL,
                               headers=self.headers, params=params).json()
        except requests.exceptions.RequestException:
            print(f'Server error')
            raise HTTPError

        return res.get('_embedded').get('items')

    def get_file_info(self, name=None, is_folder=False):
        """Поиск информации о файле(-ах) с указанными именем
        Args:
            name: Имя разыскиваемого файла или папки
            is_folder: Является ли разыскиваемый объект папкой?
        Return: Лист найденных файлов
        """

        params = {'limit': '10000',
                  'fields': 'items.name,items.type,items.path'}
        try:
            res = requests.get(f'{self.URL}/files',
                               headers=self.headers, params=params).json()
        except requests.exceptions.RequestException:
            raise HTTPError

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
        Args:
            file: json объект, описывающий желаемый файл
            path: Путь к папке, куда установится файл
        """
        if not path:
            path = 'Downloads'
        if not os.path.isdir(path):
            os.mkdir(path)

        try:
            request = requests.get(
                f'{self.URL}/download?path={file.get("path")}',
                headers=self.headers)
            download_url = request.json()['href']

            download_response = requests.get(download_url)
            with open(f'{path}/{file.get("name")}', 'wb') as f:
                f.write(download_response.content)
        except requests.exceptions.RequestException:
            raise HTTPError

    def download_folder(self, folder, path=None):
        """Скачивание выбранной папки на компьютер
        Args:
            folder: json объект, описывающий желаемую папку
            path: Путь к папке, куда установится содержимой указанной папки
        Return: True если успех
        """
        if not path:
            path = f'Downloads/{folder.get("name")}'
        else:
            path = path + '/' + folder.get("name")
        if not os.path.isdir(path):
            os.mkdir(path)

        try:
            files = self.search(folder.get("path"))
        except requests.exceptions.RequestException:
            raise HTTPError

        for file in files:
            if 'dir' in file.get("type"):
                self.download_folder(file, path)
            else:
                self.download_file(file, path)

        return True
