import os
import io
import csv
import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from settings import folderID

def getFilesFromGD(all, filename=None): #if all is true, then filename is not used. if all is false, then filename is used and is a required parameter.
    try:
        credentials = service_account.Credentials.from_service_account_file("credentials.json", scopes=['https://www.googleapis.com/auth/drive.readonly'])
        service = build('drive', 'v3', credentials=credentials)

        if all:

            query = f"'{folderID}' in parents"
            results = service.files().list(q=query, fields="files(id, name)").execute() #
            items = results.get('files', [])
            if not items:
                return 404, 'no files found'

            for i in range(len(items)):
                name = items[i]['name']
                if os.path.isfile(name): #checks if the file already exists in the directory.
                    with open(name, 'r') as f:
                        reader = csv.reader(f)
                        row_count = sum(1 for row in reader)
                        if row_count > 1: #if the file only has 1 row, its the header and is useless. If there is more than 1 row, it has data
                            items[i] = None #do not download files that are already in the directory. files wil not be edited after upload so all files are up-to-date.


            
        else:
            if not filename:
                return 404, 'you sent a query for 1 file but no filename was provided'
            
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader)
                    if row_count > 1: #if the file only has 1 row, its the header and is useless. If there is more than 1 row, it has data
                        return 200, 'file already downlaoded!' #do not download files that are already in the directory. files wil not be edited after upload so all files are up-to-date.
            
            query = f"'{folderID}' in parents and name='{filename}' and mimeType='text/csv'"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                return 404, 'No file was found with that filename'
            
        
        for item in items: #iterate through the files and downlaod them

            if item == None: #file already downloaded, dont do it again
                continue

            if os.path.isfile(item['name']):   
                destination = item['name'] + "_1"
            else:
                destination = item['name']
            fileID = item['id']

            request = service.files().get_media(fileId=fileID)
            fh = io.FileIO(destination, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            print(f"{destination} successfully downloaded")

            with open(destination, 'r') as f: #checks to ensure that the things downloaded are okay
                reader = csv.reader(f)
                row_count = sum(1 for row in reader)
                if row_count <= 1: #if the file only has 1 row, its the header and is useless, so delete it
                    print(f"{destination} does not have enough data, deleted.")
                    os.remove(destination) 

        return 200, 'all files requested that have data were downloaded'

    except Exception:
        error = traceback.format_exc()
        return 404, error  



# print(getFilesFromGD(all=False, filename="2024-05-22_B52.csv"))
# print(getFilesFromGD(all=True))
