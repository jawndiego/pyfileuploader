from flask import Flask, request
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings 
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv, find_dotenv
import os
import pinecone

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

load_dotenv(find_dotenv())

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

# Create the folders once and store the ids
uploads_folder_id = create_drive_folder("Uploads")
preprocessed_uploads_folder_id = create_drive_folder("Preprocessed Uploads")

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
    gfile.Upload() # Upload the file.

def process_text_file(file_path):
    # Read file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Process content with langchain
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=0
)
    chunks = splitter.split_text(content)

    embeddings = OpenAIEmbeddings(llm_model_name="text-davinci-002")
    embeddings_list = embeddings.get_embeddings(chunks)

    # Save processed content to a new file
    processed_file_path = os.path.join("/Users/lreyes/Desktop/Github/pyfileuploader/src/flask-server/temp-file-cache", f"{file_path}_processed.txt")
    with open(processed_file_path, 'w') as file:
        for embedding in embeddings_list:
            file.write(str(embedding.tolist()) + "\n")
    
    return processed_file_path

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
        
        # Here, you can send the processed files to Pinecone. Remember to remove the files afterwards
        # send_file_to_pinecone(processed_filepath)
        pinecone_vector_store = Pinecone(api_key=os.getenv('PINECONE_API_KEY'), index_name=os.getenv("PINECONE_ENV"))
        pinecone_vector_store.add_vectors(processed_filepath)
        os.remove(filepath)
        os.remove(processed_filepath)
    return {"message": "Files successfully uploaded"}, 200

if __name__ == '__main__':
    app.run(debug=True)
