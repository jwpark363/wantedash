import os, shutil
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Form, File
from typing import Annotated, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from agent.general_agent import GeneralAgent, GeneralAgentWithDB #chat, reset_agent
from lib.google_util import auth
from lib.prompt_generator import make_prompt
from lib.system_prompt import GENERAL_PROMPT
from lib.postgreasql_momory import get_chat_history, get_session_history

router = APIRouter()

load_dotenv()
project_name = 'wanted_2nd_wantedash'
os.environ['LANGSMITH_PROJECT'] = project_name
UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

creds_file = './credentials.json'
creds = auth(creds_file)

# g_agent = GeneralAgent(creds,GENERAL_PROMPT.format(**make_prompt(creds)))
g_agent = GeneralAgentWithDB(creds,GENERAL_PROMPT.format(**make_prompt(creds)))

@router.get("/reset")
def reset():
    g_agent.reset_agent(GENERAL_PROMPT.format(**make_prompt(creds)))
    return {"result":"reset"}

@router.get("/messages/{id}")
def messages(id:str):
    print(id)
    history = get_session_history(session_id=id)
    results = []
    for message in history:
        results.append(
            {
                'type':'AI' if isinstance(message, AIMessage) else 'HUMAN' if isinstance(message, HumanMessage) else 'BASE',
                'content': message.content,
                'conversation_id': message.conversation_id
            }
        )
    # print(results)
    return {"result":results}

@router.post("/chat")
async def for_student(
    id: Annotated[str, Form()],  ## session_id
    session_id: Annotated[str, Form()], ## conversation_id
    message: Annotated[str, Form()],
    file: Annotated[Optional[UploadFile], File()] = None
):
    print(f'********* {id} - {session_id}')
    print(message)
    print(file)
    # 1. 파일 로컬에 저장
    if file and file.filename:
        _name, _ext = os.path.splitext(file.filename)
        _filename = f'{_name}-{datetime.today().strftime("%Y%m%d%H%M-%f")}{_ext}'
        _file_path = os.path.join(UPLOAD_DIRECTORY, _filename)
        print('****** file upload ******',_file_path)
        try:
            ## 저장될 파일명은 기존 파일명에 "%Y%m%d%H%M-%f" 붙여 생성
            # shutil.copyfileobj를 사용해 파일을 복사합니다.
            with open(_file_path, "wb") as fp:
                shutil.copyfileobj(file.file, fp)
            message = f"{message}, 업로드 파일은 {_filename} 입니다."
        except Exception as e:
            print(f"message: 파일 업로드 중 오류 발생: {e}")
        finally:
            file.file.close()
    # 2. 메시지에 추가 : '로컬 파일 경로' 는 '저장된 파일 패스' 입니다.
    ## 세션 처리 방법 고민 필요 -> 클라이언트에서 생성하여 전송
    # cfg = {"configurable" : {"session_id" : session_id}}
    ## DB session_id, conversation_id 사용 형식
    cfg = {"configurable" : {"session_id" : id, "conversation_id":session_id}}
    result = g_agent.chat(message,cfg)
    print(result)
    return result