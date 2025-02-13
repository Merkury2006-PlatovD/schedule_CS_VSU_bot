from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import openpyxl


class GoogleSheetDownloader:
    def __init__(self, file_id, scopes=None):
        if scopes is None:
            scopes = ['https://www.googleapis.com/auth/drive.readonly']

        self.__downloader = None
        creds = service_account.Credentials.from_service_account_file(
            'google_api/vsu-cs-schedule-bot-21aef2c144f7.json', scopes=scopes)
        self.__drive_service = build('drive', 'v3', credentials=creds)
        self.__file_id = file_id
        self.__mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def __download_fresh_table(self):
        request = self.__drive_service.files().export_media(fileId=self.__file_id, mimeType=self.__mime_type)
        fh = io.FileIO('schedule.xlsx', 'wb')
        self.__downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = self.__downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    def update_table(self):
        try:
            self.__download_fresh_table()
            self.__format_fresh_table()
        except Exception as e:
            print(f"Error during update: {e}")

    @staticmethod
    def __format_fresh_table():
        try:
            file_path = 'schedule.xlsx'
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            rows_to_delete = [3, 4, 21, 38, 55, 72, 89]
            for row in sorted(rows_to_delete, reverse=True):
                ws.delete_rows(row)
            wb.save('schedule.xlsx')
            print("Table updated and saved as 'modified_schedule.xlsx'.")
        except Exception as e:
            print(f"Error during formatting: {e}")
