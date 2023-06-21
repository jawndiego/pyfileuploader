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
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.prompts.chat import HumanMessage, SystemMessage
from langchain.schema import Document
from langchain.retrievers import PineconeHybridSearchRetriever
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

    index = pinecone.Index(index_name)
    upsert_response = index.upsert(
    vectors=[
        (
            f"document-{i}", # Unique vector ID 
            embedding, # Dense vector values
            {"page_content": chunk} # Vector metadata
        ) for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list))
    ]
)
    print("Upsert response:", upsert_response)
    # get ready for semantic search 


    

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
    
# def get_similar_docs(query, k=2):
#     # Convert the query string into a vector
#     embeddings = OpenAIEmbeddings()
#     query_vector = embeddings.embed_documents([query])[0]  # Get the first (and only) vector

#     # Perform the similarity search
#     index = pinecone.Index(index_name)
#     query_result = index.query(queries=[query_vector], top_k=k)

#     # Fetch the actual vectors from the Pinecone index
#     similar_docs = [index.fetch(ids=[vector_id])[0] for vector_id in query_result.ids]

#     return similar_docs

def get_similar_docs(query, k=2):
    # Generate embeddings for the query
    embeddings = OpenAIEmbeddings()
    query_embedding = embeddings.embed_documents([query])

    # Use the Pinecone index to find similar documents
    index = pinecone.Index(index_name)
    query_result = index.query(queries=[query_embedding[0]], top_k=k)

    # Check if query_result is None or if query_result.ids and/or query_result.metadata are None
    if query_result is None or query_result.ids is None or query_result.metadata is None:
        return []

    # Convert the QueryResult to a list of Document objects
    similar_docs = [Document(id=id, text=metadata['page_content']) for id, metadata in zip(query_result.ids, query_result.metadata)]
    return similar_docs

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
        return {"error": str(e)}, 500
    
def get_answer(query):
    try:
        # Perform semantic search against Pinecone index
        top_documents = get_similar_docs(query, k=5)

        # Initialize the language model
        model_name = "gpt-3.5-turbo"
        model = ChatOpenAI(model_name=model_name)

        # Build context
        chat_history = []
        question = HumanMessage(content=str(query))  # Format the question as a HumanMessage

        print('Question:', question)
        print('Chat History:', chat_history)
        print('Documents:', top_documents)

        # Run the chat model using retrieved top documents
        messages = [SystemMessage(content=doc.text) for doc in top_documents] + [question]
        response = model(messages)

        print('Response:', response)

        print('get_answer completed successfully')
        return response.content  # Access the content of the AIMessage object
    except Exception as e:
        print('Error getting answer:', e)
        return {"error": str(e)}



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