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

WRITING_SPREADSHEET_ID = "1sJS1RSb-0xu2bYe5tgCuN2E98bDt21ULIufejaQ89IM"
WRITING_RANGE_NAME = "Processed Infos!A:E"

def get_today_date ():
    today = date.today()
    return f"{str(today.day).zfill(2)}/{str(today.month).zfill(2)}/{today.year}"

def get_today_rows (values:List[List], today:str, last_id: int):
    new_rows = []

    for row in values:
        if row[0] == today:
            last_id += 1
            row.insert(0, last_id)
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

def get_new_insertions (last_id: int):

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=READING_SPREADSHEET_ID,
                                    range=READING_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        today = get_today_date()

        new_lines = get_today_rows (values, today, last_id)

        return new_lines


    except HttpError as err:
        print(err)

def get_last_row ():

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()

        result = sheet.values().append(spreadsheetId=WRITING_SPREADSHEET_ID,
                                    range=WRITING_RANGE_NAME, 
                                    valueInputOption="USER_ENTERED",
                                    body = {"values":[]}).execute()
        appended_row = result.get('updates').get("updatedRange").replace("'", "")

        aux = appended_row.split("!A")
        aux[1] = str(int(aux[1]) - 1)
        last_row = "!A".join(aux)

        return last_row
    
    except HttpError as err:
        print(err)

def get_last_id ():

    last_row = get_last_row ()

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=WRITING_SPREADSHEET_ID,
                                    range=last_row).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        return values[0][0]
    
    except HttpError as err:
        print(err)

def insert_new_rows (new_insertions):
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

    body = {
        "values": new_insertions
    }

    result = sheet.values().append(spreadsheetId=WRITING_SPREADSHEET_ID,
                                   range=WRITING_RANGE_NAME, 
                                   valueInputOption="USER_ENTERED",
                                   body = body).execute()
    values = result.get('updates')

creds = authentication_process()

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    last_id = int(get_last_id ())

    new_insertions = get_new_insertions(last_id)

    insert_new_rows (new_insertions)


if __name__ == '__main__':
    main()