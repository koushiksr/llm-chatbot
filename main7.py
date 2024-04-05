import os
import pickle
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "AIzaSyDbqUJwrU4txlAWOKr9QN_-dqLgtpB1VUQ"

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

def chatbot():
    db = load_database()

    if db is None:
        st.error("Database not found.")
        return

    st.title("Chatbot")
    with st.form("chat_form"):
        query = st.text_input("You:", key="input_query")
        submit_button = st.form_submit_button(label="Send")
        if query and submit_button:
            response = process_query_and_generate_response(query, db)
            if "error" in response:
                st.error(response["error"])
            else:
                # Define CSS styles for chat bubbles
                # st.markdown(
                #     """
                #     <style>
                #     .user-bubble {
                #         background-color: #DCF8C6;
                #         padding: 10px;
                #         border-radius: 10px;
                #         margin: 5px 50px 5px 5px;
                #         text-align: right;
                #     }
                #     .bot-bubble {
                #         background-color: #E3E3E3;
                #         padding: 10px;
                #         border-radius: 10px;
                #         margin: 5px 5px 5px 50px;
                #         text-align: left;
                #     }
                #     </style>
                #     """
                # )

                # Display user message
                # st.markdown(f'<div class="user-bubble">{query}</div>', unsafe_allow_html=True)

                # Display bot response
                # st.title('🎈 App Name')
                st 
                st.write('Hello world!')
                st.markdown(f'<div class="bot-bubble">{response.content}</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    chatbot()
