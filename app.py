from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
import sqlite3
import cv2
import numpy as np
import face_recognition
from werkzeug.utils import secure_filename  # Add this import
import base64


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'


# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gpa REAL NOT NULL,
            encoding BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gpa = request.form['gpa']

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

            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encoding = encodings[0].tobytes()
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("INSERT INTO students (name, age, gpa, encoding) VALUES (?, ?, ?, ?)",
                          (name, age, gpa, encoding))
                conn.commit()
                conn.close()
                flash('Student added successfully.')
            else:
                flash('No face found in the image.')

    return render_template('create.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # Extract base64-encoded image data from the form
        image_data = request.form['image_data']
        image_data = image_data.split(",")[1]  # Remove the data type part

        # Decode the base64 string and convert to NumPy array
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Convert to OpenCV format

        # Get face encodings for the uploaded image
        unknown_encoding = face_recognition.face_encodings(img_np)

        # If no face is found, display a message
        if len(unknown_encoding) == 0:
            flash('No face found in the image!')
            return redirect(url_for('test'))

        unknown_encoding = unknown_encoding[0]  # Use the first encoding

        # Retrieve all known students' encodings from the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT name, age, gpa, encoding FROM students")
        results = c.fetchall()
        conn.close()

        # Convert the known encodings back to NumPy arrays (they must have 128 dimensions)
        known_encodings = []
        for name, age, gpa, enc in results:
            try:
                enc_array = np.frombuffer(enc, dtype=np.float64)
                if enc_array.shape[0] == 128:  # Ensure the encoding has the right shape
                    known_encodings.append((name, age, gpa, enc_array))
                else:
                    print(f"Skipped an encoding with incorrect shape: {enc_array.shape}")
            except Exception as e:
                print(f"Error converting encoding: {e}")
        
        # Extract just the face encodings for comparison
        known_face_encodings = [enc[3] for enc in known_encodings]

        # Check if the face matches any known encodings
        matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding)

        # Default values for unknown faces
        name, age, gpa = "Unknown", None, None

        if True in matches:
            # Get the index of the matched face and retrieve the details
            match_index = matches.index(True)
            name, age, gpa = known_encodings[match_index][:3]
        else:
            # Store the face encoding in session for later use (if unknown)
            session['unknown_encoding'] = unknown_encoding.tolist()  # Convert array to list for session storage
            session['img_data'] = image_data  # Store the image data
            return render_template('results.html', name="Unknown", age=None, gpa=None, add_to_db=True)

        return render_template('results.html', name=name, age=age, gpa=gpa, add_to_db=False)

    return render_template('test.html')

@app.route('/add_to_db', methods=['POST'])
def add_to_db():
    # Get the form data and the stored face encoding
    name = request.form['name']
    age = request.form['age']
    gpa = request.form['gpa']
    encoding = np.array(session.get('unknown_encoding')).tobytes()  # Convert back to bytes

    # Insert the new person's details and encodinginto the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, age, gpa, encoding) VALUES (?, ?, ?, ?)",
              (name, age, gpa, encoding))
    conn.commit()
    conn.close()

    # Clear the session data after adding to the database
    session.pop('unknown_encoding', None)
    session.pop('image_data', None)

    flash(f'{name} added successfully to the database.')
    return redirect(url_for('index'))



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
