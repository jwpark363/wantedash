import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents.output_parsers.tools import ToolAgentAction
from typing import List, Dict
from lib.system_prompt import GENERAL_PROMPT
from lib.google_util import auth
from lib.tools.google.toolkit import GoogleToolkit
load_dotenv()
project_name = 'wanted_2nd_wantedash'
os.environ['LANGSMITH_PROJECT'] = project_name
## 1. agent 만들기
system_prompt = GENERAL_PROMPT
llm = ChatOpenAI(model='gpt-4.1-mini', temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    ("placeholder", "{chat_history}"),
    ("human","{question}"),
    ("placeholder","{agent_scratchpad}")  ## Agent 사용 결과 처리용?
])
# tool
toolkit = GoogleToolkit(creds = auth('./credentials.json'))
google_tools = toolkit.get_tools()
# agent
agent = create_openai_tools_agent(
    llm = llm,
    tools = google_tools,
    prompt = prompt
)
## executor
executor = AgentExecutor(
    agent = agent,
    tools = google_tools,
    return_intermediate_steps=True,
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

# def chat(answer, config):
#     result = agent_history.invoke({
#         "question" : answer
#         },
#         config= config
#     )    
#     return result

def chat(answer, config):
    result = agent_history.invoke({
        "question" : answer
        },
        config= config,
    )
    print('*** intermediate check', len(result['intermediate_steps']))
    if result['intermediate_steps'] and result['intermediate_steps'][0] \
        and isinstance(result['intermediate_steps'][0][0],ToolAgentAction):
        print('*** clean stores ')
        stores[config['configurable']['session_id']].messages = stores[config['configurable']['session_id']].messages[-3:]
    return result