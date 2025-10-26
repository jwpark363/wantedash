import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# --- 페이지 설정 ---
st.set_page_config(
    page_title="📄 파일 기반 AI 에이전트",
    page_icon="🤖",
    layout="wide"
)

# --- OpenAI API 키 설정 ---
# secrets.toml 파일을 사용하거나, 직접 입력할 수 있습니다.
try:
    # Streamlit Cloud 배포용 (secrets.toml)
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except FileNotFoundError:
    # 로컬 테스트용
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", 
        type="password",
        placeholder="sk-..."
    )

# --- 핵심 기능 함수 ---
def get_ai_response(api_key, messages):
    """AI 모델을 호출하여 응답을 반환하는 함수"""
    if not api_key:
        st.error("OpenAI API 키를 입력해주세요.")
        return None
        
    try:
        # LangChain을 사용하여 LLM 모델 초기화
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
        
        # 메시지 객체를 올바른 형식으로 전달
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        st.error(f"AI 호출 중 오류가 발생했습니다: {e}")
        return None

def process_uploaded_file(uploaded_file):
    """업로드된 파일을 읽어 텍스트로 변환하는 함수"""
    if uploaded_file is None:
        return ""
    try:
        # 다양한 파일 타입 처리 (여기서는 txt만 간단히 처리)
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        # 추가적으로 PDF, DOCX 등의 처리를 위한 로직을 넣을 수 있습니다.
        else:
            return f"지원하지 않는 파일 형식입니다: {uploaded_file.type}"
    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
        return ""

# --- UI 구성 ---
st.title("🤖 파일 기반 AI 에이전트")
st.caption("파일을 업로드하고 파일 내용에 대해 질문해보세요.")

# 사이드바에 파일 업로더 추가
with st.sidebar:
    st.header("파일 업로드")
    uploaded_file = st.file_uploader(
        "분석할 파일을 선택하세요.", 
        type=['txt'] # 지원할 파일 형식 지정
    )
    if uploaded_file:
        st.success(f"'{uploaded_file.name}' 파일이 업로드되었습니다.")

# --- 대화 기록 초기화 및 관리 ---
# session_state에 대화 기록이 없으면 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록을 화면에 표시
for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# --- 사용자 입력 처리 ---
prompt = st.chat_input("메시지를 입력하세요...")

if prompt:
    # 1. 파일 내용 처리
    file_content = ""
    if uploaded_file:
        file_content = process_uploaded_file(uploaded_file)
        
    # 2. 사용자 입력을 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. AI 응답 생성 준비
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            # 시스템 메시지를 동적으로 구성
            system_prompt = "당신은 유능한 AI 어시스턴트입니다."
            if file_content:
                system_prompt += f"\n\n사용자가 업로드한 파일 내용은 다음과 같습니다:\n---파일 내용 시작---\n{file_content}\n---파일 내용 끝---"

            # AI에 전달할 전체 메시지 구성
            # 시스템 프롬프트 + 이전 대화 기록 + 현재 사용자 질문
            messages_for_ai = [SystemMessage(content=system_prompt)] + st.session_state.messages
            
            # 4. AI 응답 요청 및 표시
            ai_response = get_ai_response(openai_api_key, messages_for_ai)
            
            if ai_response:
                st.markdown(ai_response)
                # AI 응답을 대화 기록에 추가
                st.session_state.messages.append(AIMessage(content=ai_response))
            else:
                st.warning("AI로부터 응답을 받지 못했습니다.")