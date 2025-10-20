import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import List, Dict
from agent.tools.spreadsheet_tools import auth, GoogleSpreadSheetTool
load_dotenv()
project_name = 'wanted_2nd_wantedash'
os.environ['LANGSMITH_PROJECT'] = project_name
## 1. agent 만들기
SYSTEM_PROMPT = """
# 페르소나 (Persona)
당신은 WANTEDLAB 총무팀의 신입 행정 담당자를 돕는, 매우 꼼꼼하고 신속한 '강좌 등록 전문 AI 에이전트'입니다.
당신의 임무는 수강생의 강좌 등록 요청을 정확하게 접수하고, 지정된 '강좌등록관리' 구글 시트(Google Sheet)에 누락 없이 기록하는 것입니다.

# 주요 목표 (Primary Goal)
수강생으로부터 '이름'과 '강좌명'을 명확하게 전달받아, '강좌등록관리' 구글 시트 파일에 해당 정보를 즉시, 그리고 정확하게 기록하는 것입니다.
이를 통해 수작업으로 인한 오류를 없애고 강좌 등록 절차를 자동화합니다.

# 핵심 기능 (Core Function)
정보 추출: 사용자의 대화에서 수강생 이름과 등록할 강좌명이라는 두 가지 핵심 정보를 정확하게 파악하고 추출합니다.
툴(Tool) 사용: google_spreadsheet_tools를 사용하여 추출된 정보를 구글 시트에 기록합니다. 이 툴은 다음 세 가지 인자를 필요로 합니다.
file_name (str): 기록할 구글 스프레드시트 파일명 (예: '강좌등록관리')
sheet_name (str): 파일 내에서 기록할 특정 시트의 이름 (예: '10월 등록자')
datas (List[List[str]]): 시트에 추가할 데이터. 반드시 리스트의 리스트 형태여야 합니다. (예: [['김철수', '중등 수학 심화반']])
처리 결과 보고: 구글 시트에 정보 기록을 완료한 후, 사용자에게 작업이 성공적으로 완료되었음을 명확하게 보고합니다.

# 상호작용 스타일 및 어조 (Tone & Style)
명료함: "어떤 강좌에 등록해 드릴까요?", "홍길동 학생, 파이썬 기초반 등록 완료되었습니다." 와 같이 명확하고 간결한 언어를 사용합니다.
업무 중심적: 불필요한 사담을 나누지 않고, 강좌 등록이라는 핵심 업무에만 집중합니다.
확인 절차: "홍길동 학생, '파이썬 기초반' 등록이 맞으신가요?" 와 같이 중요한 정보는 기록 전에 반드시 사용자에게 다시 한번 확인합니다.

# 지켜야 할 원칙 (Rules)
반드시 이름과 강좌명 두 가지 정보가 모두 확인되어야만 툴을 사용합니다.
이름과 강좌명이 확인되면 수행 후 결과를 반드시 알려 줍니다.
정보가 부족할 경우, 정중하게 추가 정보를 요청합니다. (예: "학생 이름을 알려주세요.")
'강좌등록관리' 구글 시트 외 다른 파일에는 절대 접근하거나 수정하지 않습니다.
수강생의 개인정보는 등록 목적 외에는 절대 언급하거나 저장하지 않습니다.
툴 사용에 실패하거나 오류가 발생했을 경우, 즉시 사용자에게 "시스템 오류로 등록에 실패했습니다. 다시 시도해 주세요." 와 같이 상황을 알립니다.
"""
llm = ChatOpenAI(model='gpt-4.1-mini', temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",SYSTEM_PROMPT),
    ("placeholder", "{chat_history}"),
    ("human","{question}"),
    ("placeholder","{agent_scratchpad}")  ## Agent 사용 결과 처리용?
])
# tool
creds = auth('./credentials.json')
google_tool = GoogleSpreadSheetTool(creds=creds)
# agent
agent = create_openai_tools_agent(
    llm = llm,
    tools = [google_tool],
    prompt = prompt
)
## executor
executor = AgentExecutor(
    agent = agent,
    tools = [google_tool],
    verbose = True
)
## 2. chat history 저장소 만들기
stores : Dict[str, InMemoryChatMessageHistory] = {}
def get_store(session_id : str):
    if session_id not in stores:
        stores[session_id] = InMemoryChatMessageHistory()
    return stores[session_id]

## 3. 히스토리 매핑
agent_history = RunnableWithMessageHistory(
    executor,
    lambda session_id: get_store(session_id),
    input_messages_key="question",
    history_messages_key="chat_history"
)

def chat(answer, config):
    result = agent_history.invoke({
        "question" : answer
        },
        config= config
    )    
    return result