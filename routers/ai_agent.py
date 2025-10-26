import os, shutil
from fastapi import APIRouter, UploadFile, Form, File
from typing import Annotated, Optional
from pydantic import BaseModel
from agent.general_agent import chat

router = APIRouter()

UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

class Item(BaseModel):
    message: str

@router.post("/chat")
async def for_student(
    message: Annotated[str, Form()],
    file: Annotated[Optional[UploadFile], File()] = None
):
    print(message)
    print(file)
    # 1. 파일 로컬에 저장
    if file:
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        print('****** file upload ******',file_path)
        try:
        # file.file은 UploadFile 객체 내부의 실제 파일 스트림(file-like object)입니다.
        # shutil.copyfileobj를 사용해 파일을 복사합니다.
            with open(file_path, "wb") as fp:
                shutil.copyfileobj(file.file, fp)
            message = f"{message}, 업로드 파일은 {file_path} 입니다."
        except Exception as e:
            print(f"message: 파일 업로드 중 오류 발생: {e}")
        finally:
            file.file.close()
    # 2. 메시지에 추가 : '로컬 파일 경로' 는 '저장된 파일 패스' 입니다.
    ## 세션 처리 방법 고민 필요 -> 클라이언트에서 생성하여 전송
    cfg = {"configurable" : {"session_id" : "student-123"}}
    result = chat(message,cfg)
    print(result)
    return result