import requests.exceptions

from GoogleDrive import GoogleDrive
from YandexDisk import YandexDisk


class CloudsHandler:
    def __init__(self):
        self.google = GoogleDrive()
        self.yandex = YandexDisk()

    def check_google(self, directory='all'):
        """Displays files in the given directory
           Returns: List of files
        """
        if directory == 'all':
            dir_id = 'all'
        elif directory == 'root':
            dir_id = 'root'
        else:
            possible_dirs = self.google.get_file_info(directory,
                                                      is_folder=True)
            if len(possible_dirs) > 1:
                print('!!! Было найдено несколько папок с одинаковым именем. '
                      'Уточните ID папки.')
                dir_id = input("ID: ")
                print()
            elif len(possible_dirs) == 0:
                print(f"Не нашлось папок {directory}")
                raise requests.exceptions.HTTPError
            else:
                dir_id = possible_dirs[0].get('id')

        return self.google.search(directory_id=dir_id)

    def check_yandex(self, directory='all'):
        """Displays files in the given directory
           Returns: List of files"""
        if directory == 'all':
            files = self.yandex.get_file_info()
        elif directory == 'root':
            files = self.yandex.search('/')
        else:
            possible_dirs = self.yandex.get_file_info(directory,
                                                      is_folder=True)

            if len(possible_dirs) > 1:
                for pos_dir in possible_dirs:
                    print(
                        f"{pos_dir.get('name')}, путь: {pos_dir.get('path')}")
                print('!!! Было найдено несколько папок с одинаковым именем. '
                      'Уточните путь папки.')
                desired_path = input("Путь: ")
            elif len(possible_dirs) == 0:
                print(f'Не нашлось папок с именем {directory}')
                raise requests.exceptions.HTTPError
            else:
                desired_path = possible_dirs[0].get('path')

            files = self.yandex.search(desired_path)

        return files

    def download_google(self, is_dir, name):
        """Downloads a file or a folder
        Args:
            is_dir: Does selected object is folder?
            name: name of the selected file of folder
        Returns : Nothing
        """
        possible_files = self.google.get_file_info(name=name, is_folder=is_dir)
        desired_file = None
        if len(possible_files) > 1:
            print(
                '!!! Было найдено несколько файлов/папок с одинаковым именем. '
                'Уточните ID.')
            file_id = input("ID: ")
            for file in possible_files:
                if file_id == file.get("id"):
                    desired_file = file
                    break
            print()
        elif len(possible_files) == 0:
            print(f"Не нашлось файлов {name}")
            raise requests.exceptions.HTTPError
        else:
            desired_file = possible_files[0]

        if is_dir:
            if self.google.download_folder(folder=desired_file):
                print("Folder downloaded")
            else:
                print("Something went wrong")
        else:
            print(self.google.download_file(file=desired_file))

    def download_yandex(self, is_dir, name):
        """Downloads a file or a folder
        Args:
            is_dir: Does selected object is folder?
            name: name of the selected file of folder
        Returns : Nothing
        """
        possible_files = self.yandex.get_file_info(name, is_dir)
        desired_file = None

        if len(possible_files) > 1:
            print(
                '!!! Было найдено несколько файлов/папок с одинаковым именем. '
                'Уточните путь.')
            file_id = input("Путь: ")
            for file in possible_files:
                if file_id == file.get("path"):
                    desired_file = file
                    break
            print()
        elif len(possible_files) == 0:
            print(f'Не нашлось файлов/папок с именем: {name}')
            raise requests.exceptions.HTTPError
        else:
            desired_file = possible_files[0]

        if is_dir:
            if self.yandex.download_folder(desired_file):
                print("Folder downloaded")
            else:
                print("Something went wrong")
        else:
            print(self.yandex.download_file(desired_file))

    def upload_google(self, is_folder, path):
        """Uploads a file or a folder
        Args:
            is_folder: Does selected object is folder?
            path: path to the uploaded file or folder
        Returns : Nothing
        """
        if is_folder == 'file':
            return self.google.upload_file(path=path, parents_id='root')
        elif is_folder == 'folder':
            return self.google.upload_folder(path=path, parents_id='root')
        else:
            print(f'Wrong parameter {is_folder}')

    def upload_yandex(self, is_folder, path):
        """Uploads a file or a folder
        Args:
            is_folder: Does selected object is folder?
            path: path to the uploaded file or folder
        Returns : Nothing
        """
        if is_folder == 'file':
            self.yandex.upload_file(path_result='/', path_source=path,
                                    replace=True)
        elif is_folder == 'folder':
            self.yandex.upload_folder(save_path='', load_path=path)
        else:
            print(f'Wrong parameter {is_folder}')
