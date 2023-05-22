import os.path
import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

#    If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


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


def make_q_parameters(name, extension, parent):
    q = ''
    if name != '':
        q = q + f"and name='{name}' "
    if extension:
        q = q + f"and {extension} "
    if parent != 'all':
        q = q + f"and '{parent}' in parents "

    return q


def get_path_for_file(service, file):
    # Get the parent folder IDs
    parent_ids = file.get("parents")

    # Get the path to the file
    path_parts = []

    while parent_ids:
        parent_id = parent_ids[0]
        parent_metadata = service.files().get(fileId=parent_id,
                                              fields="id, name, "
                                                     "parents").execute()
        parent_name = parent_metadata.get("name")
        path_parts.insert(0, parent_name)
        parent_ids = parent_metadata.get("parents")

    file_path = "/".join(path_parts) + '/'
    return file_path


class GoogleDrive:
    def __init__(self):
        self._creds = authorize()
        self.service = build('drive', 'v3', credentials=self._creds)

    def build_drive_service(self):
        return build('drive', 'v3', credentials=self._creds)

    def download_file(self, file, path=None):
        """Downloads a file
        Args:
            file: ID of the file to download
            path: path for downloading file
        Returns : String.
        """

        if not self._creds:
            self._creds = authorize()
        if not path:
            path = 'Downloads'
        if not os.path.isdir(path):
            os.mkdir(path)

        try:
            request = self.service.files().get_media(fileId=file.get("id"))
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

    def download_folder(self, folder, path=None):
        if not self._creds:
            self._creds = authorize()
        if not path:
            path = f'Downloads/{folder.get("name")}'
        else:
            path = path + '/' + folder.get("name")
        if not os.path.isdir(path):
            os.mkdir(path)

        try:
            files = self.search(directory_id=folder.get("id"))

            for file in files:
                if 'folder' in file.get("mimeType"):
                    self.download_folder(folder=file, path=path)
                else:
                    self.download_file(file=file, path=path)

        except HttpError as error:
            print(F'An error occurred: {error}')
            return False

        return True

    def search(self, directory_id, extension=None, name=''):
        """Search files in drive location"""

        try:
            files = []
            page_token = None

            q = "trashed=false " \
                f"and 'me' in owners " + \
                make_q_parameters(name=name, extension=extension,
                                  parent=directory_id)

            while True:
                res = self.service.files().list(q=q,
                                                spaces='drive',
                                                fields='nextPageToken, '
                                                       'files(id, name, '
                                                       'mimeType, '
                                                       'parents)',
                                                pageToken=page_token).execute()

                files.extend(res.get('files', []))
                page_token = res.get('nextPageToken', None)
                if page_token is None:
                    break

            for file in files:
                file['path'] = get_path_for_file(self.service, file)

        except HttpError as error:
            print(F'An error occurred: {error}')
            files = None

        return files

    def get_file_info(self, name, is_folder=False):
        try:
            files = []
            page_token = None

            q = f"trashed=false " \
                f"and 'me' in owners "
            if name == 'root':
                q = q + f"and 'root' in parents "
            else:
                q = q + f"and name='{name}' "

            if is_folder:
                q = q + f"and mimeType='application/vnd.google-apps.folder' "

            while True:
                res = self.service.files().list(q=q,
                                                spaces='drive',
                                                fields='nextPageToken, '
                                                       'files(id, name, '
                                                       'mimeType, parents)',
                                                pageToken=page_token).execute()

                files.extend(res.get('files', []))

                page_token = res.get('nextPageToken', None)
                if page_token is None:
                    break

            if len(files) > 1:
                for file in files:
                    if 'folder' in file.get("mimeType"):
                        print(
                            F'{file.get("name")}, '
                            F'путь: {get_path_for_file(self.service, file)}, '
                            F'ID: {file.get("id")}, Папка')
                    else:
                        print(
                            F'{file.get("name")}, '
                            F'путь: {get_path_for_file(self.service, file)}, '
                            F'ID: {file.get("id")}, Файл')

        except HttpError as error:
            print(F'An error occurred: {error}')
            files = None

        return files

    def upload_file(self, path, parents_id):
        try:
            name = os.path.basename(path)
            file_meta = {'name': name, 'parents': [parents_id]}
            media_content = MediaFileUpload(path)

            existing_files = self.search(directory_id=parents_id, name=name)
            if len(existing_files) == 0:
                self.service.files().create(body=file_meta,
                                            media_body=media_content).execute()
            else:
                self.service.files().update(fileId=existing_files[0].get('id'),
                                            media_body=media_content).execute()
        except Exception as e:
            print("Ошибка")
            return False

        print(f'File {name} successfully uploaded')
        return True

    def upload_folder(self, path, parents_id):
        try:
            name = os.path.basename(path)
            folder_meta = {'name': name,
                           'mimeType': 'application/vnd.google-apps.folder',
                           'parents': [parents_id]}

            existing_folders = self.search(directory_id=parents_id,
                                           extension='mimeType="application'
                                                     '/vnd.google-apps'
                                                     '.folder"',
                                           name=name)

            if len(existing_folders) == 0:
                folder = self.service.files().create(body=folder_meta,
                                                     fields='id').execute()
            else:
                folder = {'id': existing_folders[0].get('id')}

            for element in os.listdir(path):
                file_path = os.path.join(path, element)

                if os.path.isdir(file_path):
                    self.upload_folder(path=file_path,
                                       parents_id=folder.get('id'))
                else:
                    self.upload_file(path=file_path,
                                     parents_id=folder.get('id'))

        except Exception as e:
            print("ОШИБКА")
            return False

        print(f'Folder {name} successfully uploaded')
        return True
