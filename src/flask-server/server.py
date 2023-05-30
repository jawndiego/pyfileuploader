from flask import Flask
from flask_restful import reqparse, Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

@app.route("/", methods=["GET"])
def Page():
    return {"message": "Welcome to the Home page!"}

@app.route("/members", methods=["GET"])
def members():
    return {"members": ["Member1", "Member2","Member3"]}

if __name__ == "__main__":
    app.run(debug=True)
