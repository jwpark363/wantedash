# LLM + 구글 드라이브 이용한 시트 자동화 시스템
- Chat GPT 4.1 LLM 모델 사용
- Langchain
- Google Drive Tool 개발
    1. 폴더 검색 및 생성
    2. 파일 검색 및 생성
    3. 스프레드시트의 특정 시트 마지막줄에 CSV 문자열 추가
    4. 파일(docx, doc) 파일 업로드

    <img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/main.png" width=300>

### 시스템 구조
- 프론트 : html + javascript
- 백엔드 : fastapi, langchain, gpt 4.1, google driver tools
<img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/system.png">

### 역할
- 관리자 : 구글드라이브의 기준 정보 파일 관리
- 백앤드 에이전트 : langchain + gpt 4.1 + google driver tools
    1. 기준 정보 이용한 시스템 프롬프트 생성
    <img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/config.png">
    2. 에이전트 초기화
    3. 수강생의 정보를 입력받아 기준 정보 기준으로 업무 처리
    <img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/example.png" height="350">

```python
## 구글 툴 사용
toolkit = GoogleToolkit(creds = auth('./credentials.json'))
google_tools = toolkit.get_tools()
## 툴킷에 스프레드시트에 csv 문자열 넣기와 docx 파일 업로드 툴 포함되어 있음
## 필요에 따라 추가 툴 생성하여 툴킷 get_tools 함수에 추가하여 사용

## 구글 툴 코드
class PathData(BaseModel):
    """google api new spreadsheet tool : file name"""
    path_name: str =  Field(..., description="file or folder path, ex)/wantedash/study/스터디")

class NewSpreadsheet(BaseTool):
    """
    Create a new spreadsheet file in the specified folder
    path_name : str, /wantedash/study/스터디 = /wantedash/stdy 폴더에 스터디 스프레드시트 파일 생성
    """
    name: str = "new_spreadsheet"
    description: str = "A tool to find file or folder."
    args_schema: Type[BaseModel] = PathData
    ## auth
    creds : Credentials = Field(description='credential object for google api')

    def _run(self, path_name: str) -> str:
        results = mkfile(self.creds, path_name, MimeType.spreadsheet)
        return tool_result(results)
        # if results.id:
        #     return f"FILE_ID : {spread_id}"
        # else:
        #     return "알 수 없는 오류 발생 : 생성 실패"

class SheetData(BaseModel):
    """google api add csv data to spreadsheet tool : file name, csv data"""
    path_name: str =  Field(..., description="spreadsheet file path, ex)/wantedash/study/스터디")
    sheet_name: str = Field(..., description="sheet name to add csv data to")
    csv_string: str = Field(..., description="csv format data to add to spreadsheet, ex)이름,과정,전화번호")
class AppendSpreadSheet(BaseTool):
    """Add a single line of CSV data into a spreadsheet"""
    name: str = "append_csvstring_to_spreadsheet"
    description: str = "A tool to find file or folder."
    args_schema: Type[BaseModel] = SheetData
    ## auth
    creds : Credentials = Field(description='credential object for google api')
    
    def _run(self, path_name: str, sheet_name: str, csv_string: str) -> str:
        ## search spreadsheet file
        results = mkfile(self.creds,path_name,MimeType.spreadsheet)
        ## append csv_string to spreadsheet
        results = append_datas_to_spreadsheet(self.creds, results.id, sheet_name, csv_string)
        return tool_result(results)