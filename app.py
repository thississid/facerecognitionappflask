from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import sqlite3
import cv2
import face_recognition
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encoding BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# Upload face image to store in DB
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Face recognition process
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            encoding = encodings[0]
            name = request.form.get('name', 'Unknown')
            
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, encoding.tobytes()))
            conn.commit()
            conn.close()

            flash(f'{name} face stored successfully!')
        else:
            flash('No face found in the image!')

        return redirect(url_for('index'))

# Recognize face from uploaded image
@app.route('/recognize', methods=['POST'])
def recognize_face():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    unknown_image = face_recognition.load_image_file(file_path)
    unknown_encoding = face_recognition.face_encodings(unknown_image)

    if len(unknown_encoding) == 0:
        flash('No face found in the image!')
        return redirect(url_for('index'))
    
    unknown_encoding = unknown_encoding[0]

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM faces")
    results = c.fetchall()

    conn.close()

    known_encodings = [(name, np.frombuffer(enc)) for name, enc in results]
    matches = face_recognition.compare_faces([enc[1] for enc in known_encodings], unknown_encoding)

    name = "Unknown"
    if True in matches:
        match_index = matches.index(True)
        name = known_encodings[match_index][0]

    return render_template('results.html', name=name)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
