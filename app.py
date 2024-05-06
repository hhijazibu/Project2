from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from PIL import Image
import pytesseract
import pdfplumber
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from transformers import pipeline
import spacy
from collections import Counter
import spacy
import re
import yake
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_pymongo import PyMongo
from threading import Thread
import queue






class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization")

app = Flask(__name__)
task_queue = queue.Queue()
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)
app.secret_key = 'your_super_secret_key'
app.config['UPLOAD_FOLDER'] = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

nltk.download('vader_lexicon')

def worker():
    while True:
        task = task_queue.get()
        if task is None:  
            break
        print(f"Processing task: {task}")
        task_queue.task_done()

thread = Thread(target=worker)
thread.start()



users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def perform_sentiment_analysis(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() if page.extract_text() else ""
    return text

def extract_text(filepath, filename):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return pytesseract.image_to_string(Image.open(filepath))
    elif filename.lower().endswith('.txt'):
        with open(filepath, 'r') as file:
            return file.read()
    elif filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    return ""

def summarize_text(text):
    chunk_size = 623
    overlap = 200
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]
    
    summarized_text = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summarized_text.append(summary[0]['summary_text'])
    
    final_summary = ' '.join(summarized_text)
    return final_summary

def preprocess_text(text):
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_keywords(text, num_keywords=10):
    clean_text = preprocess_text(text)
    doc = nlp(clean_text)
    keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk) < 4 and not any(token.is_stop for token in chunk)]
    return list(set(keywords))[:num_keywords]



@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        existing_user = users.find_one({'username': form.username.data})
        if existing_user is None:
            hashed_password = generate_password_hash(form.password.data)
            users.insert_one({'username': form.username.data, 'password': hashed_password})
            flash('Registration successful, please login.')
            return redirect(url_for('login'))
        flash('Username already exists')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = mongo.db.users
        user = users.find_one({'username': form.username.data})
        if user and check_password_hash(user['password'], form.password.data):
            session['username'] = user['username']
            return redirect(url_for('upload'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = extract_text(filepath, filename)
            sentiment = perform_sentiment_analysis(text)
            processed_text = preprocess_text(text)  
            summary = summarize_text(text) if text else "No text to summarize"
            keywords = extract_keywords(processed_text)  
            task_queue.put(('analyze', filepath))
            flash('Upload successful, processing started.')
            return render_template('upload.html', sentiment=sentiment, text=processed_text, summary=summary, keywords=keywords)
    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
@app.route('/shutdown')
def shutdown():
    task_queue.put(None)  
    thread.join() 
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)




if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)



