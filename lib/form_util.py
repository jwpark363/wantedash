import os, gspread, json
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

### Google Form 관련 API

SCOPES = ["https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive"]
# DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
## 인증 처리
def auth(credentials_file:str) -> Credentials:
    """Authentication processing and saving token file to local folder"""
    _SCOPES = SCOPES
    creds : Credentials | None = None
    # creds: Optional[Credentials] = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", _SCOPES)
    # 유효한 인증 정보가 없으면, 사용자에게 로그인을 요청
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, _SCOPES)
            creds = flow.run_local_server(port=0)
        # 다음 실행을 위해 인증 정보를 저장합니다.
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def spreadsheet_to_dataframe(creds:Credentials, spreadsheet_id, sheet_name):
    """
    스프레드시트의 데이터 읽어 DataFrame 생성
    """
    df = pd.DataFrame()
    try:
        # service = build("sheets", "v4", credentials=creds)
        print('*** start')
        client = gspread.authorize(creds)
        print('*** client : ', client)
        spreadsheet = client.open_by_key(spreadsheet_id)
        print('*** spreadsheet : ', spreadsheet)
        worksheet = spreadsheet.worksheet(sheet_name)
        print('*** worksheet : ', worksheet)
        data = worksheet.get_all_records()
        print('*** data : ', data)
        df = pd.DataFrame(data)
    except HttpError as error:
        print(f"an error occured: {error}")
        ## if exception, empty dataframe
    return df

def create_google_form(creds:Credentials, form_json:str, question_json:str):
    service = build(
        "forms",
        "v1",
        credentials=creds
        # http=creds.authorize(Http()),
        # discoveryServiceUrl=DISCOVERY_DOC,
        # static_discovery=False,
    )
    # 폼 기본 정보 / 생성 json(form_json)은 title 만 필요, 나머지 이후 업데이트
    ## form json string을 dict 객체로 변환 필요
    # 폼 생성 요청
    print('*** creating google form')
    form_result = (
        service.forms()
        .create(body=json.loads(form_json)).execute()    
    )
    
    print(form_result)
    print('*** add questions to google form')
    question_result = (
        service.forms()
        .batchUpdate(
            formId=form_result["formId"],
            body=json.loads(question_json)
        ).execute()
    )
    print(question_result)
    result = service.forms().get(formId=form_result["formId"]).execute()
    print("*** create google form result ***")
    print(result)