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


def check_files_in(directory='all_folders', files_type='any'):
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
    if directory != 'all_folders':
        dir_id = GoogleDrive.get_id_from_name(service, directory)

        if not dir_id:
            print(f"Wrong directory: {directory}")
            return
    else:
        dir_id = 'all_folders'

    if files_type not in possible_extensions:
        print(f"Unsupported extension: {files_type}")
        return

    files = GoogleDrive.search_files(service, dir_id,
                                     possible_extensions[files_type])


def download_file(name):
    service = GoogleDrive.build_service(creds)
    file_id = GoogleDrive.get_id_from_name(service, name)


if __name__ == '__main__':
    fire.Fire()
