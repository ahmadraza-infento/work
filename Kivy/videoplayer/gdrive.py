import os
import io
import pickle
import os.path
from loges import Logger
from utils import Configs
from threading import Thread
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload 
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



class DriveDownloader():
    def __init__(self) -> None:
        '''Configuration'''
        self._FOLDER_ID = Configs.FOLDER #'1ExjYdfMGNCfRjBKmsAXcd2OoYhQzD_S1'  # here to write folder id from google drive
        self._SCOPES    = ['https://www.googleapis.com/auth/drive.readonly']
        self._LCL_FOLDER= Configs.LCL_FOLDER
        self._creds     = None
        if not os.path.exists(self._LCL_FOLDER):
            os.makedirs(self._LCL_FOLDER)

    def _connect(self):
        """Download all files in the specified folder in Google Drive."""
        
        if self._creds is None:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self._creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self._SCOPES)
                self._creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self._creds, token)

        service = build('drive', 'v3', credentials=self._creds)
        return service

    def _download_file(self, item, service):
        file_id     = item['id']
        file_name   = item['name']
        lcl_fname   = os.path.join(self._LCL_FOLDER, file_name)
        if not os.path.exists( lcl_fname ):
            request = service.files().get_media(fileId=file_id)
            with open(lcl_fname, 'wb') as fh:
                downloader  = MediaIoBaseDownload(fh, request)
                done        = False
                while done is False:
                    status, done = downloader.next_chunk()
                    Logger.info("Downloading %d%%." % int(status.progress() * 100))
        
        else:
            Logger.info(f"file[{file_name}] already downloaded")

    def _download_files(self, service):
        drive_files = []
        page_token = None
        while True:
            # Call the Drive v3 API
            results = service.files().list(
                                q=f"'{self._FOLDER_ID}' in parents",
                                pageSize=10, fields="nextPageToken, files(id, name)",
                                pageToken=page_token).execute()
            items = results.get('files', [])

            if not items:
                Logger.info("No files found at drive folder")
            
            else:
                Logger.info(f"{len(items)} files found ")

                for item in items:
                    drive_files.append  (item['name'])
                    self._download_file (item, service)

            page_token = results.get('nextPageToken', None)
            if page_token is None:
                Logger.info("no more page_token available")
                break
        return drive_files

    def _remove_extras(self, drive_files):
        lcl_files       = os.listdir(Configs.LCL_FOLDER)
        files_to_remove = [f for f in lcl_files if f not in drive_files] 
        for f in files_to_remove:
            try:
                os.remove(os.path.join(Configs.LCL_FOLDER, f) )
                Logger.info(f"file[{f}] removed from [{Configs.LCL_FOLDER}]")
            except Exception as e:
                Logger.exception(e, "_remove_extras", "gdrive")

    def download_files_bg(self):
        def job():
            service             = self._connect()
            self._download_files(service)

        self._th = Thread(target=job)
        self._th.start()
        
    def download_files(self):
        service             = self._connect()
        drive_files         = self._download_files(service)
        self._remove_extras(drive_files)
        


if __name__ == '__main__':
    drive_downloader = DriveDownloader()
    drive_downloader.download_files()
    _ = input("Again >>>")
    drive_downloader.download_files()
    _ = input("Again >>>")
    drive_downloader.download_files()
    _ = input("exit >>>")
