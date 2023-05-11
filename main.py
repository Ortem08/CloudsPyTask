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
    service = GoogleDrive.build_service(creds)
    if directory != 'all':
        possible_dirs = GoogleDrive.get_id_2(service, directory)
        if len(possible_dirs) > 1:
            print('Multiple files found with the same name. Please specify the file ID.')
            return
        elif not possible_dirs:
            print(f'No files found with the name: {name}')
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


def download_file(name):
    service = GoogleDrive.build_service(creds)
    file_id = GoogleDrive.get_id_from_name(service, name)


def test(name):
    service = GoogleDrive.build_service(creds)
    files = GoogleDrive.get_id_2(service, name)
    if len(files) > 1:
        print('Multiple files found with the same name. Please specify the file ID.')
        file_id = None
    elif not files:
        print(f'No files found with the name: {name}')
        file_id = None
    else:
        # Get the file ID
        file_id = files[0].get('id')
        print('File ID: {}'.format(file_id))


if __name__ == '__main__':
    fire.Fire()
