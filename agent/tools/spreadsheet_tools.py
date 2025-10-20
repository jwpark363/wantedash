import os
import google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, ToolException


SCOPES = ["https://www.googleapis.com/auth/drive"]
## 인증 처리
def auth(credentials_file:str) -> Credentials:
    """Authentication processing and saving token file to local folder"""
    creds : Credentials | None = None
    # creds: Optional[Credentials] = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # 유효한 인증 정보가 없으면, 사용자에게 로그인을 요청
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # 다음 실행을 위해 인증 정보를 저장합니다.
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def _print(message):
    print('****** Google Spread Sheet Tool ******')
    print(message)
    print('****** Google Spread Sheet Tool ******')

class SpreadsheetDatas(BaseModel):
    """Comma-separated format data"""
    file_name: str =  Field(..., description="spread sheet file name")
    sheet_name: str = Field(..., description="sheet name to save data")
    datas: List[List[str]] = Field(..., description="comma-separated data to be stored in the sheet")

class GoogleSpreadSheetTool(BaseTool):
    """A tool to find spreadsheets and add data to them."""
    name: str = "google_spreadsheet_tools"
    description: str = "A tool to find spreadsheets and add data to specific sheets."
    args_schema: Type[BaseModel] = SpreadsheetDatas
    ## auth
    creds : Credentials = Field(description='credential object for google api')
    # driver_service : Resource = Field(description="service for google driver api")
    # sheet_service : Resource = Field(description="service for google sheet api")
    
    
    def _get_or_create_spreadsheet(self, file_name: str) -> str:
        """
        Checks for the existence of a Google Sheet file with the given name. If not, creates a new file and returns its file ID.
        """
        # 1. credential
        try:
            driver_service = build("drive", "v3", credentials=self.creds)
            # 1. check file exist
            query = (
                f"name = '{file_name}' and "
                f"mimeType = 'application/vnd.google-apps.spreadsheet' and "
                f"trashed = false"
            )
            response = driver_service.files().list(q=query, pageSize=1, fields="files(id)").execute()
            files = response.get("files", [])
            if files:
                file_id = files[0].get("id")
                _print(f"Found existing file '{file_name}'. (ID: {file_id})")
                return file_id
            else:
                # 2. new file
                file_metadata = {
                    "name": file_name,
                    "mimeType": "application/vnd.google-apps.spreadsheet",
                }
                file = driver_service.files().create(body=file_metadata, fields="id").execute()
                file_id = file.get("id")
                _print(f"a new file '{file_name}' has been created. (ID: {file_id})")
                return file_id
        except HttpError as error:
            _print(f"an error occured: {error}")
            raise ToolException('Error creating spreadsheet file')

    def _append_datas_to_sheet(self, spreadsheet_id: str, sheet_name: str, datas: list):
        """
        Checks if a specific sheet exists, creates it if it doesn't exist, and then adds data to it.
        """
        try:
            sheet_service = build("sheets", "v4", credentials=self.creds)
            # 1. check sheet_name
            sheet_metadata = sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            sheet_exists = False
            for sheet in sheets:
                if sheet.get("properties", {}).get("title", "") == sheet_name:
                    sheet_exists = True
                    break
            # 2. if not sheet, add new sheet
            if not sheet_exists:
                body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    }]
                }
                sheet_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body
                ).execute()
                _print(f"add new sheet '{sheet_name}'")
            # 3. append data from last rows
            body = {'values': datas}
            result = sheet_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            return f"append data completed : {result.get('updates').get('updatedCells')} datas"
        except HttpError as error:
            raise ToolException(f'Error creating spreadsheet file : {error}')
            
    def _run(
        self,
        file_name: str,
        sheet_name: str,
        datas: List[List[str]]
    ) -> str:
        """
        1. 파일명, 시트명, 데이터 체크
        2. 파일명이 없을 경우 newfile, 시트명이 없을 경우 sheet1
        3. 데이터가 없을 경우 파일만 생성
        """
        file_name = file_name.strip()
        sheet_name = sheet_name.strip()
        if len(file_name) == 0:
            file_name = 'newfile'
        if len(sheet_name):
            sheet_name = 'sheet1'
        try:
            spreadsheet_id = self._get_or_create_spreadsheet(file_name)
            return self._append_datas_to_sheet(spreadsheet_id,sheet_name,datas)
        except Exception as e:
            _print(f'Error : {str(e)}')
            raise ToolException(f'Error creating spreadsheet file : {e}')