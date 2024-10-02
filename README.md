# Face Recognition Flask App

This project is a Flask-based web application for face recognition. The app allows users to upload face images, stores their face encodings in a SQLite database, and recognizes faces from webcam images by comparing them with the stored encodings.

## Features

- Upload a face image and store the face encoding in a database.
- Recognize faces from a webcam snapshot using face encodings stored in the database.
- Simple user interface with Flask templates and image upload functionality.

## Requirements

To run this application, you need to have the following installed:

- Python 3.6+
- Flask
- OpenCV
- face_recognition (a Python library built on dlib)
- SQLite (for storing face encodings)
- NumPy
- Werkzeug (for secure file upload)
- Jinja2 (Flask's default templating engine)

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd facerecognitionappflask
