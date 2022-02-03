from __future__ import print_function
from datetime import date, datetime

import os.path
import sys
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from report_sender import send_error

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
PARTNER_SPREADSHEET_ID = '1DRp_uIevrEPHTiQ_gHquyxM2sDOfwVXk4sBH2LSS5VY'
PARTNER_RANGE_INFOS = 'Infos!P4:AA'

SERVICE_SPREADSHEET_ID = "1sJS1RSb-0xu2bYe5tgCuN2E98bDt21ULIufejaQ89IM"
SERVICE_RANGE_ALL = "Processed Infos!A:G"

def get_today_date () -> str:
    """
    ## Get Today Date
    This function is responsible to get the current date and return it as a string formated as dd/mm/yyyy.
    """
    try:
        today = date.today()
        today = today.strftime("%d/%m/%Y")
    
    except Exception as e:
        error_message = f"""        
        {e}
        <br><br>
        Something went wrong retrieving today's date.
        <br><br>
        Please check the get_today_date function and see if the 'datetime' library is correctly installed in your machine.
        """

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    else:
        return today

def get_today_rows (values: List[List], today: str, last_id: int) -> List[List]:
    """
    ## Get Today Rows
    This function is responsible to catch the rows from the partner sheet and filter it according to some requirements.
    The requirements are:
        - The row must have in it's ninth column the today date.
        - The row must have the either the value "G" or the value "P" in the eighth column
    ---
    #### Parameters:
        - values: This parameter is basically the sheet tha was read from the partner spreadsheet. It is a list of lists, or a matrix if you prefer, containing every value from the relevant columns in the sheet.
        - today: This parameter is today's date in a string, formated as dd/mm/yyyy.
        - last_id: This parameter is retrieved through the get_last_id function. It is an integer representing the ID that will be inserted in the new row at the service spreadsheet.
    ---
    #### Returns:
        - The new rows to be inserted in the service spreadsheet.
    """
    new_rows = []

    try:
        for row in values:
            if row[8] == today:
                if row[7] == "G":
                    last_id += 1
                    new_rows.append( [ last_id, 
                                    row[0], 
                                    "Fechado_Ganho", 
                                    "" if len (row) < 12 else row[-1], 
                                    "integration@ficticious.com", 
                                    f"{ today } { datetime.now().strftime('%H:%M:%S') }", 
                                    "Chamado Encerrado" ] )
                
                elif row[7] == "P":
                    last_id += 1
                    new_rows.append( [ last_id, 
                                    row[0], 
                                    "Fechado_Perdido", 
                                    row[-1], 
                                    "integration@ficticious.com", 
                                    f"{ today } { datetime.now().strftime('%H:%M:%S') }", 
                                    "Chamado Encerrado" ] )
    
    except IndexError as err:
        error_message = f"""        
        {err}
        <br><br>
        Something went wrong acessing the sheet rows due to at least one of them not having all expected data.
        <br><br>
        Please check your clients table and see if all rows are correctly filled and there is no data missing."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)
        send_error(error_message)

        sys.exit(1)

    else:
        return new_rows

def authentication_process () -> Credentials:
    """
    ## Authentication Process
    This function is responsible to update the API credentials, so the bot will always have acess to the required spreadsheets. It returns the retrieved credentials for the API.
    """

    creds = None

    try:
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
    
    except FileNotFoundError as fileError:
        error_message = f"""        
        {fileError}
        <br><br>
        There was a problem during the authentication process due to a file missing.
        <br><br>
        Please check the credentials folder present in this robot directory."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)
        send_error (error_message)

        sys.exit(1)

    else:
        return creds

def get_new_insertions () -> List[List]:
    """
    ## Get New Insertions
    This function is integrates get_today_date and get_today_rows. It retrieves all rows from the partner spreadsheet and sends it to be filtered. When the filtering is done, it returns the filtered rows to be inserted.
    """

    last_id = int(get_last_id ())

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=PARTNER_SPREADSHEET_ID,
                                    range=PARTNER_RANGE_INFOS).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        today = get_today_date()

        new_lines = get_today_rows (values, today, last_id)

    except HttpError as req_err:
        error_message = f"""        
        {req_err}
        <br><br>
        There was a problem during the API request process in the function get_new_insertions.
        <br><br>
        Please check for connectivity issues, clients spreadsheet availability or see if the API service is activated on Google Cloud."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    else:
        return new_lines

def get_last_row () -> str:
    """
    ## Get Last Row
    This function is responsible to catch the last row from the service spreadsheet. It's approach is a little different to the others, but it is for performance enhancement.

    Since we cannot knwon how many rows there is in the service spreadsheet (and it can be a lot), we use the ".append" method instead of ".get", so the requisition time is constant, and use the returned success object to retrieve wich row has been updated.
    """

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()

        result = sheet.values().append(spreadsheetId=SERVICE_SPREADSHEET_ID,
                                    range=SERVICE_RANGE_ALL, 
                                    valueInputOption="USER_ENTERED",
                                    body = {"values":[]}).execute()
        appended_row = result.get('updates').get("updatedRange").replace("'", "")

        aux = appended_row.split("!A")
        if ( int(aux[1]) - 1 ) > 1:
            aux[1] = str(int(aux[1]) - 1)
            last_row = "!A".join(aux)
        
        else:
            aux[1] = str(int(aux[1]))
            last_row = "!A".join(aux)
    
    except HttpError as req_err:
        error_message = f"""        
        {req_err}
        <br><br>
        There was a problem during the API request process in the function get_last_row.
        <br><br>
        Please check for connectivity issues, service spreadsheet availability or see if the API service is activated on Google Cloud."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""
        
        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    else:
        return last_row

def get_last_id () -> str:
    """
    ## Get Last ID
    This function is used along with get_last_row, so it can retrieve the last row id from the service spreadsheet more quickly.
    """

    last_row = get_last_row ()

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SERVICE_SPREADSHEET_ID,
                                    range=last_row).execute()
        values = result.get('values', [])
    
    except HttpError as req_err:
        error_message = f"""        
        {req_err}
        <br><br>
        There was a problem during the API request process in the function get_last_id.
        <br><br>
        Please check for connectivity issues, service spreadsheet availability or see if the API service is activated on Google Cloud."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    else:
        if not values:
            print('No data found.')
            return 0

        return values[0][0]

def insert_new_rows (new_insertions: List[List]):
    """
    ## Insert New Rows
    This function is responsible to insert the retrieved rows from the partner spreadsheet to the service spreadsheet. It appends the new rows at the end of the table.

    ---
    #### Parameters:
        - new_insertions: This parameter is a list containing all of the new rows to be inserted at the service spreadsheet.
    """

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()

        body = {
            "values": new_insertions
        }

        result = sheet.values().append(spreadsheetId=SERVICE_SPREADSHEET_ID,
                                    range=SERVICE_RANGE_ALL, 
                                    valueInputOption="USER_ENTERED",
                                    body = body).execute()
        values = result.get('updates')
    
    except HttpError as req_err:
        error_message = f"""        
        {req_err}
        <br><br>
        There was a problem during the API request process in the function get_last_id.
        <br><br>
        Please check for connectivity issues, service spreadsheet availability or see if the API service is activated on Google Cloud."""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)
        send_error (error_message)

        sys.exit(1)
    
    else:
        print (values)



def main():

    new_insertions = get_new_insertions()

    insert_new_rows (new_insertions)



creds = authentication_process()

if __name__ == '__main__':
    main()
