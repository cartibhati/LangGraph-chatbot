import streamlit as st
from langgraph_database_backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessageChunk
import uuid #(we can generate more than one threads)

#______________utility functions_______________________

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id #(gives random thread id everytime)

def reset_chat():
    #generate new thread id
    thread_id = generate_thread_id()

    #store it in the session
    st.session_state['thread_id']=thread_id

    #add thread to chat_thread list also
    add_thread(st.session_state['thread_id'])

    #empty the message history
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

#if you give this function a thread id , it will extract all messages
#and will give you the chat history
def load_conversation(thread_id):
    return chatbot.get_state(config ={'configurable': {'thread_id': thread_id}}).values['messages']


#___________________session setup_________________________


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=retrieve_all_threads()

add_thread(st.session_state['thread_id'])

#______________side bar UI______________________________________

#Adding a sidebar with title
st.sidebar.title('LangGraph Chatbot')

#A start chat button
if st.sidebar.button('New chat'):
    reset_chat()

# a title named 'My conversations'
st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    #displaying all the threads in sidebar
     if st.sidebar.button(str(thread_id)):
         st.session_state['thread_id']=thread_id
         messages = load_conversation(thread_id)

         
         #since the message_history has the list of dicxtionaroes , so we gotta write some code to prevent compaibility issues in the future
         #to get it into this format:-#{'role': 'user', 'content': 'Hi'}
                                    #{'role': 'assistant', 'content': 'Hi=ello'}
         temp_messages = []

         for msg in messages:
            if isinstance(msg,HumanMessage):
                 role='user'
            else:
                role='assistant'
            temp_messages.append({'role':role,'content':msg.content})
         st.session_state['message_history']=temp_messages
            

#__________________Main UI_______________________________


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)


    # st.session_state -> dict -> 
    CONFIG = {'configurable': {'thread_id': str(st.session_state['thread_id'])}} #(generating dynamic thread id)

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
        message_chunk.content
        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )
        if isinstance(message_chunk, AIMessageChunk) and message_chunk.content
    )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})