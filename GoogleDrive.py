import os.path
import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def build_drive_service(creds):
    return build('drive', 'v3', credentials=creds)


def authorize():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def download_file(file, creds=None, path=None):
    """Downloads a file
    Args:
        file: ID of the file to download
        creds: authorization data for user
        path: path for downloading file
    Returns : String.
    """

    if not creds:
        creds = authorize()
    if not path:
        path = 'Downloads'
    if not os.path.isdir(path):
        os.mkdir(path)

    try:
        service = build_drive_service(creds)

        """if "spreadsheet" in file.get("mimeType"):
            sheets_service = build_sheets_service(creds)
            request = service.files().export_media(fileId=file.get("id"),
                                                      mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        elif "document" in file.get("mimeType"):
            docs_service = build_docs_service(creds)
            request = service.files().export_media(fileId=file.get("id"),
                                                    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        else:"""
        request = service.files().get_media(fileId=file.get("id"))
        final_file = io.BytesIO()
        downloader = MediaIoBaseDownload(final_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        final_file.seek(0)
        with open(
                f'{path}/{file.get("name")}',
                'wb') as f:
            f.write(final_file.getvalue())

    except HttpError as error:
        print(F'An error occurred: {error}')

    return f'{file.get("name")} downloaded'


def download_folder(folder, creds=None, path=None):
    if not creds:
        creds = authorize()
    if not path:
        path = f'Downloads/{folder.get("name")}'
    else:
        path = path + '/' + folder.get("name")
    if not os.path.isdir(path):
        os.mkdir(path)

    try:
        service = build_drive_service(creds)
        files = search_files(service, folder.get("id"))

        for file in files:
            if 'folder' in file.get("mimeType"):
                download_folder(file, creds, path)
            else:
                download_file(file, creds, path)

    except HttpError as error:
        print(F'An error occurred: {error}')
        return False

    return True


def search_files(service, directory_id, extension=None, name=''):
    """Search files in drive location"""

    try:
        files = []
        page_token = None

        q = "trashed=false " \
            f"and 'me' in owners " + \
            make_q_parameters(name, extension, directory_id)

        while True:
            response = service.files().list(q=q,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, fullFileExtension, mimeType, parents)',
                                            pageToken=page_token).execute()

            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        if not files:
            print("No such files")

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files


def get_path_for_file(service, file):
    # Get the parent folder IDs
    parent_ids = file.get("parents")

    # Get the path to the file
    path_parts = []

    while parent_ids:
        parent_id = parent_ids[0]
        parent_metadata = service.files().get(fileId=parent_id,
                                              fields="id, name, parents").execute()
        parent_name = parent_metadata.get("name")
        path_parts.insert(0, parent_name)
        parent_ids = parent_metadata.get("parents")

    file_path = "/".join(path_parts) + '/'
    return file_path


def get_file_info(service, name, is_folder=False):
    try:
        files = []
        page_token = None

        q = f"trashed=false " \
            f"and 'me' in owners " \
            f"and name='{name}' "

        if is_folder:
            q = q + f"and mimeType='application/vnd.google-apps.folder' "

        while True:
            response = service.files().list(q=q,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, fullFileExtension, mimeType, parents)',
                                            pageToken=page_token).execute()

            files.extend(response.get('files', []))

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        if len(files) > 1:
            for file in files:
                if 'folder' in file.get("mimeType"):
                    print(F'{file.get("name")}, путь: {get_path_for_file(service, file)}, ID: {file.get("id")}, Папка')
                else:
                    print(F'{file.get("name")}, путь: {get_path_for_file(service, file)}, ID: {file.get("id")}, Файл')

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files


def make_q_parameters(name, extension, parent):
    q = ''
    if name != '':
        q = q + f"and name='{name}' "
    if extension:
        q = q + f"and {extension} "
    if parent != 'all':
        q = q + f"and '{parent}' in parents "

    return q
