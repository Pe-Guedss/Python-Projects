from pprint import pprint
from modules.drive_service import create_drive_service

API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = create_drive_service(API_NAME, API_VERSION, SCOPES)

pprint (dir(service))