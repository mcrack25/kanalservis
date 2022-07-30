from __future__ import print_function

import os.path

import requests
import xmltodict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_valutes():
    """Возвращает список валют"""
    r = requests.get('https://www.cbr.ru/scripts/XML_daily.asp?date_req=02/03/2022')
    return xmltodict.parse(r.text)['ValCurs']['Valute']


def get_valute(code):
    """Получает валюту по её коду"""
    for valute in get_valutes():
        if valute['CharCode'] == code:
            return valute
    return None


def convert_valute(course_value, usd_value):
    """Конвертирует валюту в рубли"""
    return float(course_value.replace(',', '.')) * int(usd_value)


def get_sheet_data(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, SCOPES):
    """Возвращает данные из google sheet"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        return result.get('values', [])
    except HttpError as err:
        print(err)
