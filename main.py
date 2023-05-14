import fire
import os

import GoogleDrive

possible_extensions = {'folder': 'mimeType="application/vnd.google-apps'
                                 '.folder"',
                       'text': '(mimeType="text/plain" or '
                               'mimeType="application/pdf" or '
                               'mimeType="application/msword" or '
                               'mimeType="application/vnd.openxmlformats'
                               '-officedocument.wordprocessingml.document")',
                       'table':
                           '(mimeType="application/vnd.openxmlformats'
                           '-officedocument.spreadsheetml.sheet" or '
                           'mimeType="application/vnd.google-apps'
                           '.spreadsheet" or '
                           'mimeType="application/vnd.ms-excel")',
                       'audio': 'mimeType contains "audio/"',
                       'video': 'mimeType contains "video/"',
                       'image': 'mimeType contains "image/"',
                       'any': '(mimeType contains "text/" or mimeType '
                              'contains "audio/" or mimeType contains '
                              '"video/" or mimeType contains "image/" or '
                              'mimeType contains "application/")'
                       }

creds = GoogleDrive.authorize()


def check(directory='all', files_type='any', name=''):
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
    service = GoogleDrive.build_drive_service(creds)
    if directory == 'root':
        dir_id = directory
    elif directory != 'all':
        possible_dirs = GoogleDrive.get_file_info(service, directory, is_folder=True)
        if len(possible_dirs) > 1:
            print('!!! Было найдено несколько папок с одинаковым именем. '
                  'Уточнитните ID папки.')
            dir_id = input("ID: ")
            print()
        elif not possible_dirs:
            print(f'Не нашлось папок с именем: {directory}')
            return
        else:
            dir_id = possible_dirs[0].get('id')
    else:
        dir_id = 'all'

    if files_type not in possible_extensions:
        print(f"Unsupported extension: {files_type}")
        return

    files = GoogleDrive.search_files(service, dir_id,
                                     possible_extensions[files_type], name)
    for file in files:
        if "folder" in file.get("mimeType"):
            print(F'Папка: {file.get("name")}, '
                  F'путь: {GoogleDrive.get_path_for_file(service, file)}'+'\n')
        else:
            print(F'Файл: {file.get("name")}, '
                  F'путь: {GoogleDrive.get_path_for_file(service, file)}'+'\n')


def download(is_dir_str=None, name=None):
    if is_dir_str == 'folder':
        is_dir = True
    elif is_dir_str == 'file':
        is_dir = False
    else:
        "Wrong command"
        return
    service = GoogleDrive.build_drive_service(creds)
    possible_files = GoogleDrive.get_file_info(service, name, is_folder=is_dir)
    desired_file = None
    if len(possible_files) > 1:
        print('!!! Было найдено несколько файлов/папок с одинаковым именем. '
              'Уточнитните ID.')
        file_id = input("ID: ")
        for file in possible_files:
            if file_id == file.get("id"):
                desired_file = file
                break
        print()
    elif not possible_files:
        print(f'Не нашлось файлов/папок с именем: {name}')
        return
    else:
        desired_file = possible_files[0]

    if is_dir:
        if GoogleDrive.download_folder(desired_file):
            print("Folder downloaded")
        else:
            print("Smth went wrong")
    else:
        GoogleDrive.download_file(desired_file)


if __name__ == '__main__':
    fire.Fire()
