import fire
import os

from googleapiclient.errors import HttpError

import GoogleDrive
import YandexDisk
import CloudsHandler


creds = GoogleDrive.authorize()


def check(directory='root'):
    """
    Returns a list of user's files from concrete directory on GDrive
    Parameters
    ----------
    files_type : string
        String that represents the desired type of files

    directory : string
        String that represents the name of desired directory for search

    Returns
    -------
    list
        list of found files or None
    """
    print("Подождите, выполняется поиск файлов и папок, это может занять некотрое время"+'\n')
    try:
        files = CloudsHandler.check_google(directory)
    except Exception:
        try:
            files = CloudsHandler.check_yandex(directory)
        except Exception as e:
            print("THATS WASSUP BRO, NOTHING THERE")
            return

    if len(files) == 0:
        print("Нет файлов")
    for file in files:
        if (file.get('type') == 'dir') or ('folder' in str(file.get('mimeType'))):
            print(F'Папка: {file.get("name")}, '
                  F'путь: {file.get("path")}' + '\n')
        else:
            print(F'Файл: {file.get("name")}, '
                  F'путь: {file.get("path")}' + '\n')


def download(is_dir_str='folder', name='root'):
    """
    Downloads a file/folder with {name}
    Parameters
    ----------
    is_dir_str : string
        String that represents what you want to download: 'folder' or 'file'

    name : string
        String that represents the name of desired directory or file to
        download

    Returns
    -------
    nothing
        prints 'folder downloaded' of '{filename} downloaded'
    """

    if is_dir_str == 'folder':
        is_dir = True
    elif is_dir_str == 'file':
        is_dir = False
    else:
        print(f"Wrong command {is_dir_str}")
        return

    try:
        CloudsHandler.download_google(creds, is_dir, name)
    except Exception:
        try:
            CloudsHandler.download_yandex(is_dir, name)
        except Exception:
            print("WTF BROO??!!")
            return


def upload(is_folder='folder', path='Backup'):
    """
    Uploads a file/folder with {path}, {path} can be both absolute and relative
    Parameters
    ----------
    is_folder : string
        String that represents what you want to upload: 'folder' or 'file'

    path : string
        String that represents the path of desired directory or file to
        download

    Returns
    -------
    nothing
        prints 'All staff downloaded successfully' if OK
    """

    if not os.path.exists(path):
        print("Wrong way")
        return

    service = GoogleDrive.build_drive_service(creds)

    if is_folder == 'file':
        GoogleDrive.upload_file(service, path, 'root')
    elif is_folder == 'folder':
        GoogleDrive.upload_folder(service, path, 'root')
    else:
        print(f'Wrong parameter {is_folder}')

    print('All staff was uploaded successfully')


if __name__ == '__main__':
    fire.Fire()
