import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import openpyxl


# class GoogleSheetDownloader:
#     def __init__(self, file_id, scopes=None):
#         if scopes is None:
#             scopes = ['https://www.googleapis.com/auth/drive.readonly']
#         print(os.getcwd())
#         print(os.listdir(os.getcwd()))
#         self.__downloader = None
#         creds = service_account.Credentials.from_service_account_file(
#             'src/parser/vsu-cs-schedule-bot-21aef2c144f7.json', scopes=scopes)
#         self.__drive_service = build('drive', 'v3', credentials=creds)
#         self.__file_id = file_id
#         self.__mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#
#     def __download_fresh_table(self):
#         request = self.__drive_service.files().export_media(fileId=self.__file_id, mimeType=self.__mime_type)
#         fh = io.FileIO('src/parser/schedule.xlsx', 'wb')
#         self.__downloader = MediaIoBaseDownload(fh, request)
#         done = False
#         while not done:
#             status, done = self.__downloader.next_chunk()
#             print(f"Download {int(status.progress() * 100)}%.")
#
#     def update_table(self):
#         try:
#             self.__download_fresh_table()
#             self.__format_fresh_table()
#         except Exception as e:
#             print(f"Error during update: {e}")
#
#     @staticmethod
#     def __format_fresh_table():
#         try:
#             file_path = 'src/parser/schedule.xlsx'
#             wb = openpyxl.load_workbook(file_path)
#             ws = wb.active
#             rows_to_delete = [3, 4, 21, 38, 55, 72, 89]
#             for row in sorted(rows_to_delete, reverse=True):
#                 ws.delete_rows(row)
#             wb.save('src/parser/schedule.xlsx')
#             print("Table updated and saved as 'src/parser/schedule.xlsx'.")
#         except Exception as e:
#             print(f"Error during formatting: {e}")
def update_excell():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")

    creds_dict = json.loads(credentials_json)
    print(creds_dict)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)

    # Подключаемся к API Google Drive
    drive_service = build('drive', 'v3', credentials=creds)

    # ID файла на Google Диске (Google Sheets)
    file_id = '1ryzzYpl9QN546fLQWq0lvxULcW9ygO2A5qrkDwjtNhQ'

    # Указываем MIME тип для скачивания файла как Excel
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    # Запрос на экспорт
    request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type)

    # Создание файла для записи
    fh = io.FileIO('src/parser/schedule.xlsx', 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


def format_fresh_table():
    try:
        file_path = 'src/parser/schedule.xlsx'
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        rows_to_delete = [3, 4, 21, 38, 55, 72, 89]
        for row in sorted(rows_to_delete, reverse=True):
            ws.delete_rows(row)
        wb.save('src/parser/schedule.xlsx')
        print("Table updated and saved as 'src/parser/schedule.xlsx'.")
    except Exception as e:
        print(f"Error during formatting: {e}")


def download_and_update():
    update_excell()
    format_fresh_table()
