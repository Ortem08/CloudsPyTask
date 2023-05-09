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


def main():
    pass
    # take_first_ten_files()
    # with open('Downloads/TestFile.txt', 'wb') as f:
    #    shutil.copyfileobj(download_file('19671U7PqmEDS8CIbj4cVm2D9-zQ3Yze4'),
    #                       f, length=1024)


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


def download_file(real_file_id):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
    Returns : IO object with location.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
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


def search_files(service, directory_id, extension):
    """Search file in drive location

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        files = []
        page_token = None

        while True:
            response = service.files().list(q="trashed=false "
                                              f"and {extension} "
                                              f"and 'me' in owners "
                                              f"and '{directory_id}' in parents",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, fullFileExtension, mimeType, parents)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                if "folder" in file.get("mimeType"):
                    print(F'Folder: {file.get("name")}, {file.get("id")}')
                else:
                    print(F'File: {file.get("name")}, {file.get("id")}, {file.get("parents")}')
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


def get_id_from_name(service, name):
    if name == 'root':
        return name

    try:
        response = service.files().list(q="trashed=false"
                                          f"and name='{name}'").execute()

        if not response.get('files', []):
            print(f"Wrong name: {name}")
            return None

        file = response.get('files', [])[0]

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get("id")
