from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, request, jsonify, send_file
import jwt
import stream_chat
import datetime
import json
import os
from flask_restful import Resource, Api, reqparse, abort
from werkzeug.utils import secure_filename

server_client = stream_chat.StreamChat(
    api_key="fe9wszkeesp5", api_secret="a6j639c87c2pq5k4jqf96yvudsakc2mxdj2qh3rkhescvffs5em3r6pkk9a4ypez"
)
# Flask 인스턴스 정리
app = Flask(__name__)
app.config['SECRETKEY'] = 'a6j639c87c2pq5k4jqf96yvudsakc2mxdj2qh3rkhescvffs5em3r6pkk9a4ypez'
api = Api(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient("mongodb://143.248.191.194:27017/")
db = client['madcampweek2']

@app.route('/')
def hello_world():
    return jsonify({"id":"1"}), 201

@app.route('/getalluser')
def get_all_user():
    collection =db.user
    data = list(collection.find())
    return jsonify(data)

@app.route('/getallposting')
def get_all_posting():
    collection =db.post
    data = list(collection.find())
    return jsonify(data)

#GET user/id
@app.route('/user/<param>')
def get_user(param):
    collection = db.user
    result = collection.find_one({"_id": str(param)})
    return result

@app.route('/users')
def get_user_one():
    collection = db.user
    result = collection.find_one({"_id": str(1)})
    return result

@app.route('/postdata', methods=['POST'])
def create_user():
    collection = db.user
    data = request.json
    collection.insert_one(data)
    return "1"

@app.route('/checkdata', methods=['POST'])
def create_user_1():
    collection=db.user
    data = request.json
    result = collection.find_one({'name': data['name']})
    if result is None:
        return jsonify({'token': '1'})
    else:
        token = server_client.create_token(str(result['_id']))
        return jsonify({'token': token})
    
@app.route('/mypage')
def mypage():
    collection = db.user
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401
    if token.strip()=="":
        return jsonify({'message': 'Empty token'}), 401
    try:
        # 토큰을 디코딩하여 사용자 정보 가져오기
        decoded_token = jwt.decode(token, "a6j639c87c2pq5k4jqf96yvudsakc2mxdj2qh3rkhescvffs5em3r6pkk9a4ypez" , algorithms=['HS256'])
        print(decoded_token)
        userid = decoded_token['user_id']
        result = collection.find_one({"_id": userid})
        print(result)
        # 사용자 정보 반환
        if result is not None:
            return jsonify(result)
        else:
            return jsonify({'message': 'User not found'}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/imagetoserver', methods = ['POST'])
def imagetoserver():
    collection = db.user
    token = request.headers.get('Authorization')
    decoded_token = jwt.decode(token, "a6j639c87c2pq5k4jqf96yvudsakc2mxdj2qh3rkhescvffs5em3r6pkk9a4ypez" , algorithms=['HS256'])
    userid = decoded_token['user_id']

    if 'image' not in request.files:
        return jsonify({'error' : 'No image provided'}), 400
    image = request.files['image']
    if image.filename=='':
        return jsonify({'error': 'No selected file'}), 400
    if image:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        filename = filename.replace("uploads\\", "")
        collection.update_one({'_id':userid}, {"$set": {'identityfilename': filename}})
        return jsonify({'success': filename}), 200

@app.route('/getimage/<filename>')
def getimage(filename):
    imagepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(imagepath):
        return send_file(imagepath, mimetype='image/jpeg')
    else:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/checkteam')
def checkteam():
    my_id = request.args.get('myid')
    otheruserid = request.args.get('otheruserid')
    collection = db.user
    result1 = collection.find_one({'_id':my_id})
    if result1 is not None:
        if otheruserid in result1['teamid']:
            print(1)
            return jsonify({'result':1})
    return jsonify({'result':0})

@app.route('/signup', methods = ['POST'])
def signup():
    data = request.json
    data['_id'] = str(ObjectId())
    collection=db.user
    collection.insert_one(data)
    '''return jsonify({'return':1})'''
    return jsonify({'_id': data['_id']})

@app.route('/postingtoserver', methods=['POST'])
def postingtoserver():
    image = request.files['image']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
    filename = filename.replace("uploads\\", "")
    data_str = request.form['data']
    data = json.loads(data_str)
    collection = db.post
    data['_id'] = str(collection.count_documents({}))
    data['imgfilename'] = filename
    collection.insert_one(data)
    print(data)
    return jsonify({'_id': data['_id']})


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)