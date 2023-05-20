import GoogleDrive
import YandexDisk


def check_google(directory='all'):
    service = GoogleDrive.build_drive_service(GoogleDrive.authorize())

    if directory == 'all':
        dir_id = 'all'
    elif directory == 'root':
        dir_id = 'root'
    else:
        possible_dirs = GoogleDrive.get_file_info(service, directory,
                                                  is_folder=True)
        if len(possible_dirs) > 1:
            print('!!! Было найдено несколько папок с одинаковым именем. '
                  'Уточнитните ID папки.')
            dir_id = input("ID: ")
            print()
        elif not possible_dirs:
            raise NotImplementedError
        else:
            dir_id = possible_dirs[0].get('id')

    return GoogleDrive.search(service, dir_id)


def check_yandex(directory='all'):
    if directory == 'all':
        files = YandexDisk.get_file_info()
    elif directory == 'root':
        files = YandexDisk.search('/')
    else:
        possible_dirs = YandexDisk.get_file_info(directory, is_folder=True)

        if len(possible_dirs) > 1:
            for pos_dir in possible_dirs:
                print(f"{pos_dir.get('name')}, путь: {pos_dir.get('path')}")
            print('!!! Было найдено несколько папок с одинаковым именем. '
                  'Уточнитните путь папки.')
            desired_path = input("Путь: ")
        elif len(possible_dirs) == 0:
            raise NotImplementedError
        else:
            desired_path = possible_dirs[0].get('path')

        files = YandexDisk.search(desired_path)

    return files


def download_google(creds, is_dir, name):
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
        print(GoogleDrive.download_file(desired_file))


def download_yandex(is_dir, name):
    possible_files = YandexDisk.get_file_info(name, is_dir)
    desired_file = None

    if len(possible_files) > 1:
        print('!!! Было найдено несколько файлов/папок с одинаковым именем. '
              'Уточнитните путь.')
        file_id = input("Путь: ")
        for file in possible_files:
            if file_id == file.get("path"):
                desired_file = file
                break
        print()
    elif not possible_files:
        print(f'Не нашлось файлов/папок с именем: {name}')
        return
    else:
        desired_file = possible_files[0]

    if is_dir:
        if YandexDisk.download_folder(desired_file):
            print("Folder downloaded")
        else:
            print("Smth went wrong")
    else:
        print(YandexDisk.download_file(desired_file))


def upload_google(creds, is_folder, path):
    service = GoogleDrive.build_drive_service(creds)

    if is_folder == 'file':
        GoogleDrive.upload_file(service, path, 'root')
    elif is_folder == 'folder':
        GoogleDrive.upload_folder(service, path, 'root')
    else:
        print(f'Wrong parameter {is_folder}')


def upload_yandex(is_folder, path):
    if is_folder == 'file':
        YandexDisk.upload_file(path_result='/', path_source=path, replace=True)
    elif is_folder == 'folder':
        YandexDisk.upload_folder(savepath='', loadpath=path)
    else:
        print(f'Wrpng parameter {is_folder}')
