import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import os
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename

# Initialize Firebase
cred = credentials.Certificate("path/to/your-firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'jagwirerobotic.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
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
    images = [img.to_dict() for img in images_ref]
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
    
    blob = bucket.blob(filename)
    blob.upload_from_filename(file_path)
    os.remove(file_path)
    
    db.collection('images').add({'user_id': session['user_id'], 'image_url': blob.public_url})
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

if __name__ == '__main__':
    app.run(debug=True)
