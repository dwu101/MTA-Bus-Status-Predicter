import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def uploadFileToGD(filename, folderID):
    try:
        credentials = service_account.Credentials.from_service_account_file('credentials.json')
        service = build('drive', 'v3', credentials=credentials)

        csv_file_path = filename

        file_metadata = {
            'name': filename,
            'parents': [folderID]
        }

        media = MediaFileUpload(csv_file_path, mimetype='text/csv')

        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id',
                                    supportsAllDrives=True).execute()

        return 200, 'done'
    except Exception as e:
        error = traceback.format_exc()
        return 404, error

