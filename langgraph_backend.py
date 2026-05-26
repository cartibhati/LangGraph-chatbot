from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import langchain_ollama
from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.graph.message import add_messages

# Use Ollama LLaMA3 model
llm = langchain_ollama.ChatOllama(model="llama3")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

#instead of chat.invoke , we did chat.stream for streaming the content

