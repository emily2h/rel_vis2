from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd 
import requests
import re
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1lHFnUvKJwWzOtYoGhKk1UO4q1o20QZVduoh4aya8Nzc'
SAMPLE_RANGE_NAME = 'FULL!A2:I'

wiki_head = "https://en.wikipedia.org/wiki/"


def write_entry(values, sheet):
    body = {'values':values} 
    sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=body).execute()


def write_from_URL(url, sheet, lead, show_season):
    table_class="wikitable sortable jquery-tablesorter"
    response=requests.get(url) 
    print(response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table',{'class':"wikitable"})

    df = pd.read_html(str(table))
    # convert list to dataframe
    df = pd.DataFrame(df[0])


    # A little hacky, but works for the purposes here...
    df = df.fillna("---")
    if 'Ref' in df.columns:
        df = df.drop(['Ref'], axis=1)


    place = 'Place' in df.columns
    arrivedBool = "Arrived" in df.columns

    data = []
    for i, rows in df.iterrows():
        name = rows.Name
        name = re.search(r"[^\[\]0-9]*", name).group(0)
        rows = rows.drop(labels=['Name'])

        if arrivedBool == True:
            arrived = rows.Arrived
            rows = rows.drop(labels=['Arrived'])
        else:
            arrived = "---"
        if place:
            data.append([lead, name] + rows.tolist() + [arrived, show_season])
        else:
            data.append([lead, name] + rows.tolist() + ["---", arrived, show_season])

    write_entry(data, sheet)


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # There was no need to do this with Google Sheets... I just felt like being extra.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    map_df = pd.read_csv('data/rel_map.csv')
    
    for i, rows in map_df.iterrows():
        print(rows.show_season, rows.lead)
        first_url = rows.show_season
        write_from_URL(wiki_head + first_url, sheet, rows.lead, rows.show_season)



if __name__ == '__main__':
    main()