from __future__ import print_function
from datetime import date

import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
READING_SPREADSHEET_ID = '1DRp_uIevrEPHTiQ_gHquyxM2sDOfwVXk4sBH2LSS5VY'
READING_RANGE_NAME = 'Infos!A:E'

def get_today_date ():
    today = date.today()
    return f"{str(today.day).zfill(2)}/{str(today.month).zfill(2)}/{today.year}"

def get_today_rows (values:List[List], today:str):
    new_rows = []

    for row in values:
        if row[0] == today:
            new_rows.append(row)
    
    return new_rows

def authentication_process ():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_new_insertions (creds):

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=READING_SPREADSHEET_ID,
                                    range=READING_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        today = get_today_date()

        new_lines = get_today_rows (values, today)

        return new_lines


    except HttpError as err:
        print(err)

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    
    creds = authentication_process()

    new_insertions = get_new_insertions(creds)
    print (new_insertions)



if __name__ == '__main__':
    main()