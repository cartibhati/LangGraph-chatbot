from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
import langchain_ollama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3

# Use Ollama LLaMA3 model
llm = langchain_ollama.ChatOllama(model="llama3")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

#After running this it will create a db in file directory
conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

#test
CONFIG = {'configurable':{'thread_id':'thread-1'}}

response = chatbot.invoke(
    {'messages':[HumanMessage(content = 'Whats my name?')]},
    config=CONFIG
)
print(response)
