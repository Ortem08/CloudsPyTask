import os.path
import io
import shutil

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def build_service(creds):
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


def download_file(name, real_file_id=''):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
    Returns : IO object with location.
    """
    creds = authorize()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Downloaded {int(status.progress() * 100)}%.')

        # file.seek(0)
        # with open('TestFile.txt', 'wb') as f:
        #    shutil.copyfileobj(file, f, length=1024)

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    file.seek(0)
    return file


def search_files(service, directory_id, extension, name=''):
    """Search file in drive location"""

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

            for file in response.get('files', []):
                if "folder" in file.get("mimeType"):
                    print(F'Папка: {file.get("name")}')
                    print(F'путь: {get_path_for_file(service, file)}', end='\n\n')
                else:
                    print(F'Файл: {file.get("name")}')
                    print(F'путь: {get_path_for_file(service, file)}', end='\n\n')

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


def get_id_2(service, name, concrete_id=None):
    try:
        files = []
        page_token = None

        q = f"trashed=false " + \
            f"and 'me' in owners " + \
            f"and name='{name}' "
        response = {}
        while True:
            if concrete_id:
                response_list = [service.files().get(fileId=concrete_id).execute()]
                response['files'] = response_list
            else:
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
        if len(files) > 1:
            for file in files:
                print(F'{file.get("name")}, путь: {get_path_for_file(service, file)}, ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None

    return files


def get_id_from_name(service, name):
    if name == 'root':
        return name

    try:
        response = service.files().list(q="trashed=false "
                                          f"and name='{name}'").execute()

        if not response.get('files', []):
            print(f"Wrong name: {name}")
            return None

        file = response.get('files', [])[0]

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get("id")


def make_q_parameters(name, extension, parent):
    q = ''
    if name != '':
        q = q + f"and name='{name}' "
    if parent != 'all':
        q = q + f"and '{parent}' in parents "
    if extension:
        q = q + f"and {extension} "

    return q

