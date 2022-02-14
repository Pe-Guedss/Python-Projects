from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_drive_service (api_name, api_version, *scopes) -> Credentials:
    """
    ## Authentication Process
    This function is responsible to update the API credentials, so the bot will always have acess to the required spreadsheets. It returns the retrieved credentials for the API.
    """

    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    creds = None

# =========================== Fetching the credentials ===========================
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

        There was a problem during the authentication process due to a file missing.

        Please check the credentials folder present in this robot directory."""

        print (error_message)
    except Exception as e:
        error_message = f"""        
        {e}"""

        print (error_message)

# =========================== Creating the service ===========================
    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
        print(API_SERVICE_NAME, 'service created successfully')

        return service
    except Exception as e:
        error_message = f"""        
        {e}"""
        print (error_message)
        
        return None
