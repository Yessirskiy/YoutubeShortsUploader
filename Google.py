#Had to do this cuz google package wasn't being nice
import pickle
import os
import datetime
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import config


def createService(secrets_file: str):
    CLIENT_SECRET_FILE = secrets_file
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    pickle_file = f'token_{API_NAME}_{API_VERSION}.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            creds = pickle.load(token)
    else:
        creds = None

    if (not creds) or (not creds.valid):
        if creds and (creds.expired) and (creds.refresh_token):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(config.ACCOUNTS_FOLDER, CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build(API_NAME, API_VERSION, credentials=creds)
        return service

    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt