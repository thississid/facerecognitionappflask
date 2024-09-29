from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename  # Import secure_filename
import os
import sqlite3
import cv2
import numpy as np
import face_recognition
import base64

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

# Upload and store face image in DB
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
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Load the image and create the face encoding
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            # Store the encoding in the database
            encoding = encodings[0].tobytes()  # Convert to bytes
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (filename, encoding))
            conn.commit()
            conn.close()
            flash('File uploaded and face encoded successfully.')
        else:
            flash('No face found in the image.')

    return redirect(url_for('index'))

# Recognize face from webcam image
@app.route('/recognize_webcam', methods=['POST'])
def recognize_webcam():
    # Capture base64 image from webcam
    image_data = request.form['image_data']
    # Decode base64 image
    image_data = image_data.split(",")[1]
    img_bytes = base64.b64decode(image_data)
    
    # Convert to numpy array for OpenCV and face_recognition processing
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    unknown_encoding = face_recognition.face_encodings(img_np)

    if len(unknown_encoding) == 0:
        flash('No face found in the image!')
        return redirect(url_for('index'))
    
    unknown_encoding = unknown_encoding[0]

    # Compare with known encodings in the database
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
