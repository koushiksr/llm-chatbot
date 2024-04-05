import os
import json
import pickle
from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)


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
        result1 = result.content.replace('\n', '')
        cleaned_json = result1[7:-3]
        cleaned_json_dict = json.loads(cleaned_json)
        cleaned_data = {k.replace(' ', '_'): v.replace('\n', '') if isinstance(v, str) else v for k, v in cleaned_json_dict.items()}
        return cleaned_data
    except Exception as e:
        return {"error": "Failed to process query: " + str(e)}
os.environ["GOOGLE_API_KEY"]= "AIzaSyDbqUJwrU4txlAWOKr9QN_-dqLgtpB1VUQ"
@app.route('/', methods=['POST', 'GET'])
def process_pdf_and_query():
    try:
        UPLOAD_FOLDER = 'uploads'
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        pdf_file = request.files.get('pdf')
        if not pdf_file:
            return "PDF file is missing."

        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
        pdf_file.save(pdf_path)

        query = request.args.get('query', '')
        if not query:
            return "Query parameter is missing."

        loader = PyPDFLoader(pdf_path)
        # pages = loader.load_and_split()

        db_filename = "db.pkl"
        if os.path.exists(db_filename):
            with open(db_filename, "rb") as f:
                db = pickle.load(f)
        else:
            db = None

        response = process_query_and_generate_response(query, db)

        os.remove(pdf_path)

        return jsonify(response)

    except Exception as e:
        return "Failed to process PDF and query: " + str(e)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
