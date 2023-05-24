import fire
import os

from requests.exceptions import HTTPError
from CloudsHandler import CloudsHandler


handler = CloudsHandler()


def check(directory='root'):
    """
    Prints list of user's files from concrete directory on GDrive or if it's
    unavailable from YandexDisk
    Parameters
    ----------
    directory : string
        String that represents the name of desired directory for search
    """
    print("Подождите, выполняется поиск файлов и папок, это может занять "
          "некоторое время"+'\n')
    try:
        files = handler.check_google(directory)
    except HTTPError:
        try:
            files = handler.check_yandex(directory)
        except HTTPError:
            print("Оба сервера недоступны, попробуйте позже")
            return

    if len(files) == 0:
        print("Нет файлов")
    for file in files:
        if (file.get('type') == 'dir') \
                or ('folder' in str(file.get('mimeType'))):
            print(F'Папка: {file.get("name")}, '
                  F'путь: {file.get("path")}' + '\n')
        else:
            print(F'Файл: {file.get("name")}, '
                  F'путь: {file.get("path")}' + '\n')


def download(is_dir_str='folder', name='root'):
    """
    Downloads a file/folder with {name} from GDrive or Yandex Disk on your
    computer
    Parameters
    ----------
    is_dir_str :
        String that represents what you want to download: 'folder' or 'file'

    name :
        String that represents the name of desired directory or file on your
        cloud to download
    """

    if is_dir_str == 'folder':
        is_dir = True
    elif is_dir_str == 'file':
        is_dir = False
    else:
        print(f"Wrong command {is_dir_str}")
        return

    try:
        handler.download_google(is_dir, name)
    except HTTPError:
        print("Первый сервер недоступен, пробуем подключиться ко второму")
        try:
            handler.download_yandex(is_dir, name)
        except HTTPError:
            print("Оба сервера недоступны, попробуйте позже")


def upload(is_dir_str='folder', path='Backup'):
    """
    Uploads a file/folder with {path} from your computer on GDrive or
    YandexDisk, {path} can be both absolute and relative
    Parameters
    ----------
    is_dir_str :
        String that represents what you want to upload: 'folder' or 'file'

    path :
        String that represents the path on computer of desired directory or
        file to download
    """
    if is_dir_str == 'folder':
        is_dir = True
    elif is_dir_str == 'file':
        is_dir = False
    else:
        print(f"Wrong command {is_dir_str}")
        return

    if not os.path.exists(path):
        print("Wrong way")
        return

    try:
        handler.upload_google(is_folder=is_dir, path=path)
    except HTTPError:
        print("Первый сервер недоступен, пробуем подключиться ко второму")
        try:
            handler.upload_yandex(is_folder=is_dir, path=path)
        except HTTPError:
            print("Оба сервера недоступны, попробуйте позже")
            return

    print('All staff was uploaded successfully')


if __name__ == '__main__':
    fire.Fire()
