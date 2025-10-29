import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.runnables.utils import ConfigurableFieldSpec
from lib.google_util import auth
from lib.tools.google.toolkit import GoogleToolkit
from lib.postgreasql_momory import get_chat_history

class GeneralAgent:
    def __init__(self, creds, system_prompt) -> None:
        self.creds = creds
        self.stores : Dict[str, InMemoryChatMessageHistory] = {}
        print('****** make agent ******')
        self.agent_history = self.make_agent(system_prompt)
        print(self.agent_history)

    def make_agent(self,system_prompt):
        print('**** system prompt ****')
        print(system_prompt)
        ## 1. agent 만들기
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
        def get_store(session_id : str):
            if session_id not in self.stores:
                self.stores[session_id] = InMemoryChatMessageHistory()
            return self.stores[session_id]
        ## 3. 히스토리 매핑
        return RunnableWithMessageHistory(
            executor,
            lambda session_id: get_store(session_id),
            input_messages_key="question",
            history_messages_key="chat_history"
        )

    def reset_agent(self,system_prompt):
        print('****** reset agent ******')
        self.agent_history = self.make_agent(system_prompt)        
        print(self.agent_history)
    
    def chat(self, answer, config):
        print("*** agent chat ***")
        msg = {"question" : answer}
        print('** msg : ',msg)
        print('** config : ',config)
        print(self.agent_history)
        result = self.agent_history.invoke(
            input = msg,
            config= config,
        )
        print(result)
        print("*** agent chat ***")
        print('*** intermediate check', len(result['intermediate_steps']))
        if result['intermediate_steps'] and result['intermediate_steps'][0] \
            and isinstance(result['intermediate_steps'][0][0],ToolAgentAction):
            print('*** clean stores ')
            self.stores[config['configurable']['session_id']].messages = self.stores[config['configurable']['session_id']].messages[-3:]
        return result
    
class GeneralAgentWithDB:
    def __init__(self, creds, system_prompt) -> None:
        self.creds = creds
        self.stores : Dict[str, InMemoryChatMessageHistory] = {}
        print('****** make agent ******')
        self.agent_history = self.make_agent(system_prompt)
        print(self.agent_history)

    def make_agent(self,system_prompt):
        print('**** system prompt ****')
        print(system_prompt)
        ## 1. agent 만들기
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
        ## 3. 히스토리 매핑
        return RunnableWithMessageHistory(
            executor,
            get_chat_history,
            input_messages_key="question",
            history_messages_key="chat_history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="session_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="conversation_id",
                    annotation=str,
                    name="Conversation ID",
                    description="Unique identifier for the conversation.",
                    default="",
                    is_shared=True,
                ),
            ]
        )
        # ## 3. 히스토리 매핑
        # return RunnableWithMessageHistory(
        #     executor,
        #     lambda session_id: get_store(session_id),
        #     input_messages_key="question",
        #     history_messages_key="chat_history"
        # )

    def reset_agent(self,system_prompt):
        print('****** reset agent ******')
        self.agent_history = self.make_agent(system_prompt)        
        print(self.agent_history)
    
    def chat(self, answer, config):
        print("*** agent chat ***")
        msg = {"question" : answer}
        print('** msg : ',msg)
        print('** config : ',config)
        print(self.agent_history)
        result = self.agent_history.invoke(
            input = msg,
            config= config,
        )
        print(result)
        print("*** agent chat ***")
        print('*** intermediate check', len(result['intermediate_steps']))
        ## session_id, conversation_id DB 처리 하기 때문에 필요없음
        # if result['intermediate_steps'] and result['intermediate_steps'][0] \
        #     and isinstance(result['intermediate_steps'][0][0],ToolAgentAction):
        #     print('*** clean stores ')
        #     self.stores[config['configurable']['session_id']].messages = self.stores[config['configurable']['session_id']].messages[-3:]
        return result