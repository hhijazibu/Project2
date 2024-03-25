from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from threading import Thread
import queue
import os
from PIL import Image
import pytesseract
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import uuid

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

app.config["JWT_SECRET_KEY"] = "Hassan_Project2" 
jwt = JWTManager(app)

nltk.download('vader_lexicon')

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

task_queue = queue.Queue()

def worker():
    while True:
        task = task_queue.get()
        if task is None:
            break
        text, task_id = task
        result = perform_text_analysis(text)
        print(f"Task {task_id}: {result}")
        task_queue.task_done()

thread = Thread(target=worker, daemon=True)
thread.start()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if users.find_one({"username": username}):
        return jsonify({"message": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    users.insert_one({'username': username, 'password': hashed_password})
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = users.find_one({"username": username})

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}:
            text = pytesseract.image_to_string(Image.open(filepath))
            return jsonify({"message": "File uploaded successfully", "extracted_text": text}), 201
        else:
            return jsonify({"message": "File uploaded successfully"}), 201

def perform_text_analysis(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment

@app.route('/analyze-text', methods=['POST'])
@jwt_required()
def analyze_text():
    text = request.json.get('text', '')
    if not text:
        return jsonify({"message": "No text provided"}), 400
    
    task_id = str(uuid.uuid4())
    task_queue.put((text, task_id))
    
    return jsonify({"message": "Analysis started", "task_id": task_id}), 202

if __name__ == '__main__':
    app.run(debug=True)
