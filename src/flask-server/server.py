from flask import Flask, request
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.text_splitter import TokenTextSplitter
import openai
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseDocumentTransformer, Document
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import pinecone 

# initializes pincone and fetches api key + pinecone env from .env file, user must also provide an index_name 
pinecone.init(
api_key=os.getenv('PINECONE_API_KEY'),
environment=os.getenv('PINECONE_ENV')
        )
index_name="pyneconeapp"

# gets API key from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

#loads env file 
load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

def create_drive_folder(folder_name): 
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")
    drive = GoogleDrive(gauth)

    folder_metadata = {'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Return the ID of the created folder
    return folder['id']

def upload_file_to_drive(filename, filepath, folder_id):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")
    drive = GoogleDrive(gauth)

    gfile = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
    gfile.SetContentFile(filepath)
    gfile.Upload() 

# splits text into chunks using langchain, creates embeddings, sends to pinecone
def process_text_file(file_path):
    # Read file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Process content with langchain
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=20, length_function =len,
)
    chunks = splitter.split_text(content)

    embeddings = OpenAIEmbeddings()
    embeddings_list = embeddings.embed_documents(chunks)

    documents = [Document(page_content=chunk) for chunk in chunks]
    
    index = pinecone.Index(index_name)
    upsert_response = index.upsert(
        vectors=[
            (
                "new-document-id", # Vector ID 
                embeddings_list, # Dense vector values
                {"page_content": chunk} # Vector metadata
            ) for chunk in chunks
        ]
    )

    # Saves processed content to a new file
    processed_file_path = os.path.join("/Users/lreyes/Desktop/Github/pyfileuploader/src/flask-server/temp-file-cache", f"{file_path}_processed.txt")
    with open(processed_file_path, 'w') as file:
        for embedding in embeddings_list:
            file.write(str(embedding) + "\n")
    
    return processed_file_path

def check_folder_exists(folder_name):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()

    if file_list:
        return file_list[0]['id']
    else:
        return None
    
def get_similar_docs(query, k=2, score = False):

#VIDEO    
#     index = Pinecone.from_documents(index_name)
#     if score: 
#         similar_docs = index.similarity_search_with_score(query, k=k)
#     else: 
#         similar_docs= index.similarity_search(query, k=k)
#     return similar_docs

# query = input()
# similar_docs = get_similar_docs(query)
# similar_docs

#GPT
    query = input()
    index = Pinecone.from_documents(index_name)
    query_result = index.query(queries=[query], top_k=k)
    return query_result

@app.route('/get-info', methods=['POST'])
def get_info():
    try:
        data = request.get_json()
        print('received data:', data)
        
        query = data.get('query')
        if not query:
            return {"error": "No query provided"}, 400

        # Use the get_answer function to get the answer for the query
        answer = get_answer(query)

        return {"answer": answer}, 200
    except Exception as e:
        print('Error handling request:', e)
        return {"error": "Internal server error"}, 500


def get_answer(query):
    try:
        # Fetch similar documents from Pinecone
        query_result = get_similar_docs(query)

        # Fetch the actual vectors from the Pinecone index
        index = pinecone.Index(index_name)
        input_vectors = [index.fetch(ids=[vector_id])[0] for vector_id in query_result.ids]

        # Convert vectors to documents
        input_documents = [Document(page_content=vector) for vector in input_vectors]

        # Initialize the language model
        model_name = "gpt-3.5-turbo"
        llm = OpenAI(model_name=model_name)

        # Load the question answering chain
        chain = load_qa_chain(llm, chain_type="stuff")

        # Run the chain with the input documents and question
        answer = chain.run(input_documents=input_documents, question=query)
        print('get_answer completed successfully')
        return answer.answer
    except Exception as e:
        print('Error getting answer:', e)
        return {"error": "Error getting answer"}


# Check if folders exist and get their IDs, create them if they do not exist, this is to avoid the creation of duplicate folders 
uploads_folder_id = check_folder_exists("Uploads")
if not uploads_folder_id:
    uploads_folder_id = create_drive_folder("Uploads")

preprocessed_uploads_folder_id = check_folder_exists("Preprocessed Uploads")
if not preprocessed_uploads_folder_id:
    preprocessed_uploads_folder_id = create_drive_folder("Preprocessed Uploads")

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.to_dict(flat=False)
    uploaded_files = files.get('file[]', [])
    if not uploaded_files:
        return {"error": "No files part"}, 400

    for file in uploaded_files:
        if file.filename == '':
            return {"error": "No selected file"}, 400
        filename = file.filename
        filepath = os.path.join("/Users/lreyes/Desktop/Github/pyfileuploader/src/flask-server/temp-file-cache", filename)
        file.save(filepath)

        # Pass folder_id to upload_file_to_drive function
        upload_file_to_drive(filename, filepath, uploads_folder_id)

        # Process text file
        processed_filepath = process_text_file(filepath)
        processed_filename = f'{filename}_processed.txt'

        # Upload processed file to the "Preprocessed Uploads" folder
        upload_file_to_drive(processed_filename, processed_filepath, preprocessed_uploads_folder_id)
        
        os.remove(filepath)
        os.remove(processed_filepath)
    return {"message": "Files successfully uploaded"}, 200

if __name__ == '__main__':
    app.run(debug=True)