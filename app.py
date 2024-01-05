from pymongo import MongoClient
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

# Flask 인스턴스 정리
app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://localhost:27017/")
db = client['madcampweek2']

@app.route('/')
def hello_world():
    return 'Hello, World!'

#GET user/id
@app.route('/user/<param>')
def get_user(param):
    collection = db.user
    result = collection.find_one({"_id": int(param)})
    return result


if __name__ == '__main__':
    app.run(debug=True)