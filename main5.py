import os
import json
import pickle
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

# Set the Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDbqUJwrU4txlAWOKr9QN_-dqLgtpB1VUQ"

# Function to process the query and generate response
def process_query_and_generate_response(query, db):
    if db is None:
        return {"error": "Database not found."}

    try:
        # Process the query
        docs = db.similarity_search(query)
        content = "\n".join([x.page_content for x in docs])
        qa_prompt = "Use the following pieces of context to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.----------------"
        input_text = qa_prompt + "\nContext:" + content + "\nUser question:\n" + query
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        result = llm.invoke(input_text)
        result1 = result.content.replace('\n', '')
        cleaned_json = result1[7:-3]
        cleaned_json_dict = json.loads(cleaned_json)
        cleaned_data = {k.replace(' ', '_'): v.replace('\n', '') if isinstance(v, str) else v for k, v in cleaned_json_dict.items()}
        return cleaned_data
    except Exception as e:
        return {"error": "Failed to process query: " + str(e)}

# Streamlit app
def main():
    st.title("PDF Query Processor")

    # Upload PDF file
    pdf_file = st.file_uploader("Upload your PDF", type="pdf")

    if pdf_file:
        # Process query
        query = st.text_input("Enter your query:")
        if st.button("Process Query"):
            try:
                # Save the uploaded PDF file
                with open(pdf_file.name, "wb") as f:
                    f.write(pdf_file.getbuffer())

                # Load and split the PDF document
                loader = PyPDFLoader(pdf_file.name)

                # Load database
                db_filename = "db.pkl"
                if os.path.exists(db_filename):
                    with open(db_filename, "rb") as f:
                        db = pickle.load(f)
                else:
                    db = None

                # Generate response
                response = process_query_and_generate_response(query, db)

                # Display response
                st.json(response)

                # Remove the uploaded PDF file
                os.remove(pdf_file.name)
            except Exception as e:
                st.error("Failed to process PDF and query: " + str(e))

if __name__ == '__main__':
    main()
