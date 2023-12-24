# filename: update_code.py

# This script will update your Python file in Google Drive with new code. 
# You can change the content of `uploaded_dummy` as you need.



from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Use the service account file to authenticate
creds = Credentials.from_service_account_file('google_api_credentials.json', scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# Your file id goes here
file_id = '11XlPpRe79dMXOCzrjq0LLzAJZlwsh27n'

# The new file we want to upload goes here
file_name = 'uploaded_dummy.py'
media = MediaFileUpload(file_name, mimetype='text/x-python')

# Update the file in Google Drive
file = service.files().update(fileId=file_id, media_body=media).execute()

print('File ID: %s' % file.get('id'))