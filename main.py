import fire

import GoogleDrive

possible_extensions = {'text': '(mimeType="text/plain" or '
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
                       'any': 'mimeType contains "text/" or mimeType '
                              'contains "audio/" or mimeType contains '
                              '"video/" or mimeType contains "image/" or '
                              'mimeType contains "application/" '
                       }


def check_files(extension_list):
    """
    Returns a list of user's files from GDrive
    Parameters
    ----------
    extension_list : string
        String that represents the desired extension of files

    Returns
    -------
    list
        list of found files or None
    """

    if extension_list not in possible_extensions:
        print("Unsupported extension")
        return
    files = GoogleDrive.search_files(possible_extensions[extension_list])


if __name__ == '__main__':
    fire.Fire()
