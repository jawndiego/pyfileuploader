this project uses Caisson (by salief lewis) as a starter template. the project spins up a server and handles user drag and drop files (.txt) .. saves a backup in flask-server, breaks the text files into chunks, creates vector embeddings using langchain/openai, saves a backup into your google drive, and sends vectors to pinecone index before deleting what is locally hosted.  

to use, set up a python virtual environment and pip install all dependencies in server.py 

make sure you set up an .env file with an openai api key, pinecone api key, pinecone environment. 

make sure to add an empty credentials.json in flask-server and a settings.yaml with all the google oauth2.0 stuff to allow you to create a testing environment for this app. the credentials.json temporarily saves user sessions in there. 

use pnpm to install front-end dependencies and use pnpm dev to start localhost. 

there's a bunch of directions to take this. 



Caisson is a frontend development template built upon [wagmi](https://wagmi.sh) + [ConnectKit](https://docs.family.co/connectkit) + [Tailwind](https://tailwindcss.com/) + [Next.js](https://nextjs.org)
