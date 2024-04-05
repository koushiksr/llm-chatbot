import os
import pickle
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import random
import time

os.environ["GOOGLE_API_KEY"] = "AIzaSyDbqUJwrU4txlAWOKr9QN_-dqLgtpB1VUQ"

# Function to process the query and generate response
def process_query_and_generate_response(query, db):
    if db is None:
        return {"error": "Database not found."}

    try:
        docs = db.similarity_search(query)
        content = "\n".join([x.page_content for x in docs])
        qa_prompt = "Use the following pieces of context to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.----------------"
        input_text = qa_prompt + "\nContext:" + content + "\nUser question:\n" + query
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        result = llm.invoke(input_text)
        return result
    except Exception as e:
        return {"error": "Failed to process query: " + str(e)}

def load_database():
    db_filename = "db.pkl"
    if os.path.exists(db_filename):
        with open(db_filename, "rb") as f:
            db = pickle.load(f)
        return db
    else:
        return None

def response_generator():
    response = random.choice(
        [
            "Hi! How can I help?",
            "Hey there! How can I assist you?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def chatbot():
    db = load_database()

    if db is None:
        st.error("Database not found.")
        return

    messages = st.container(height=250 )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with messages:  
            st.chat_message(message["role"]).write(message["content"])

    with st.form(key="input_form"):
        query = st.text_input(label="Enter your message here", max_chars=250, value="", help="Enter your message here",    autocomplete="off",  type="default", key="input_submit", placeholder="Enter your message here")
        submit_button = st.form_submit_button(label="Send")
        
        if query:
            st.session_state.input_disabled = True
            st.session_state.messages.append({"role": "user", "content": query})
            with messages:
                st.chat_message("user").write(query)
            response = process_query_and_generate_response(query, db)
            if "error" in response:
                st.error(response["error"])
            else:
                time.sleep(2)
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                with messages:
                    st.chat_message("assistant").write(response.content)
    

if __name__ == '__main__':
    chatbot()
