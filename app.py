import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import os
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from google.cloud import secretmanager
import json

def get_firebase_credentials():
    client = secretmanager.SecretManagerServiceClient()
    secret_name = "projects/5921455311/secrets/jag-wire-firebase/versions/latest"

    response = client.access_secret_version(name=secret_name)
    secret_data = response.payload.data.decode("UTF-8")

    # Save JSON file locally (Optional)
    with open("firebase-adminsdk.json", "w") as f:
        f.write(secret_data)

    return json.loads(secret_data)


def get_secret(secret_id="flask-secret-key", project_id="jagwirerobotic"):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode("UTF-8")

# Set Flask secret key securely
app = Flask(__name__)
app.secret_key = get_secret()

# Get Firebase credentials
firebase_credentials = get_firebase_credentials()

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'jagwirerobotic.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    try:
        user = auth.get_user_by_email(email)
        session['user_id'] = user.uid
        return redirect(url_for('dashboard'))
    except:
        return 'Login failed. User not found.', 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    images_ref = db.collection('images').where('user_id', '==', session['user_id']).stream()
    images = [{'id': img.id, **img.to_dict()} for img in images_ref]
    return render_template('dashboard.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'user_id' not in session:
        return redirect(url_for('dashboard'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('dashboard'))
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    blob = bucket.blob(f"uploads/{session['user_id']}/{filename}")
    blob.upload_from_filename(file_path)
    os.remove(file_path)
    
    image_ref = db.collection('images').add({
        'user_id': session['user_id'],
        'image_url': blob.public_url
    })
    return redirect(url_for('dashboard'))

@app.route('/delete/<path:image_id>', methods=['POST'])
def delete_image(image_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    image_ref = db.collection('images').document(image_id)
    image_doc = image_ref.get()
    if image_doc.exists:
        image_data = image_doc.to_dict()
        if image_data['user_id'] == session['user_id']:
            blob = bucket.blob(image_data['image_url'].split('/')[-1])
            blob.delete()
            image_ref.delete()
    return redirect(url_for('dashboard'))

@app.route('/sponsors')
def sponsors():
    sponsors = db.collection('sponsors').stream()
    sponsor_list = [{'name': sponsor.id, **sponsor.to_dict()} for sponsor in sponsors]
    return render_template('sponsors.html', sponsors=sponsor_list)

@app.route('/calendar')
def calendar():
    events = db.collection('events').stream()
    event_list = [{'name': event.id, **event.to_dict()} for event in events]
    return render_template('calendar.html', events=event_list)


if __name__ == '__main__':
    app.run(debug=True)
