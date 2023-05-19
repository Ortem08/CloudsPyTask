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

    return GoogleDrive.search_files(service, dir_id)


def check_yandex(directory='all'):
    if directory == 'all':
        files = YandexDisk.get_all_files()
    elif directory == 'root':
        files = YandexDisk.search('/')
    else:
        all_folders = YandexDisk.get_all_files(True)
        possible_dirs = []
        for folder in all_folders:
            if folder[0] == directory:
                possible_dirs.append(folder)

        if len(possible_dirs) > 1:
            for pos_dir in possible_dirs:
                print(f"{pos_dir[0]}, путь: {pos_dir[1]}")
            print('!!! Было найдено несколько папок с одинаковым именем. '
                  'Уточнитните ID папки.')
            desired_path = input("Путь: ")
        elif len(possible_dirs) == 0:
            raise NotImplementedError
        else:
            desired_path = possible_dirs[0][1]

        files = YandexDisk.search(desired_path)

    return files
