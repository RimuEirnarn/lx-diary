from os import environ
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

load_dotenv()
app = Flask(__name__)

client = MongoClient(environ.get("MONGODB_URI"))
database = client[environ.get("DB_NAME")]
diary = database.diary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    entries = list(diary.find({},{'_id':False}))
    return jsonify({'entries': entries, "status": "OK", "message": "Listed!"})

@app.route('/diary', methods=['POST'])
def save_diary():
    title = request.form["title"]
    content = request.form["content"]
    file = request.files['file']
    profile = request.files['profile']

    if len(title.lstrip().rstrip()) == 0 or len(content.lstrip().rstrip()) == 0:
       return jsonify({"message": "Failed, title or content has length of 0 or full of whitespaces", "status": "ERR"}), 400

    f_extension = file.filename.split('.')[-1]
    today = datetime.now()
    striped_time = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'static/file-{striped_time}.{f_extension}'
    p_extension = profile.filename.split('.')[-1]
    p_filename = f"static/profile-{striped_time}.{p_extension}"

    file.save(filename)
    profile.save(p_filename)

    entry = {
        'title': title,
        'content': content,
        'timestamp': datetime.utcnow().timestamp(),
        "image": filename,
        "profile": p_filename
    }
    diary.insert_one(entry.copy())
    return jsonify({"message": "Done!", "status": "OK", "entries": [entry]})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
