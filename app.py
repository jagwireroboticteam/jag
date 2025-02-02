from google.cloud import firestore, storage
from flask import Flask, render_template, request, redirect, url_for, session, flash
import firebase_admin
from firebase_admin import credentials, firestore
import os
from google.cloud import secretmanager
import json


app = Flask(__name__)

# Function to retrieve secret from Secret Manager
def get_secret(secret_name, project_id="jagwirerobotic"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Retrieve JSON key from Secret Manager
service_account_json = get_secret("jagwire-crediential")  # Ensure correct secret name

# Initialize Firebase Admin with the secret JSON
cred = credentials.Certificate(json.loads(service_account_json))
firebase_admin.initialize_app(cred)

db = firestore.client()


db = firestore.client()

# ✅ Cloud Storage setup
storage_client = storage.Client()
bucket_name = "jag_wire_robotic_website"
bucket = storage_client.bucket(bucket_name)

# ✅ Routes
@app.route('/')
def home():
    social_links = {
        "Instagram": {"url": "https://instagram.com/jagwirer_robotics"},
        "Facebook": {"url": "https://facebook.com/jagwirer_robotics"},
        "Twitter": {"url": "https://twitter.com/jagwirer_robotics"}
    }
    return render_template('index.html', social_links=social_links)

@app.route('/sponsors')
def sponsors():
    sponsors_ref = db.collection('sponsors').stream()
    sponsors_list = [{'name': sponsor.id, **sponsor.to_dict()} for sponsor in sponsors_ref]
    return render_template('sponsors.html', sponsors=sponsors_list)

@app.route('/donate')
def donate():
    donate_ref = db.collection('donate').stream()
    donate_list = [{'name': donate.id, **donate.to_dict()} for donate in donate_ref]
    return render_template('donate.html', sponsors=donate_list)

@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html')

@app.route('/upload')
def upload():
    images_ref = db.collection('images').stream()
    images_list = [{'file_name': img.id, 'url': img.to_dict().get('url')} for img in images_ref]
    return render_template('upload.html', images=images_list)

@app.route('/teams')
def teams():
    team_members_ref = db.collection('team_members').stream()
    team_members_list = [{'name': member.id, **member.to_dict()} for member in team_members_ref]
    return render_template('teams.html', team_members=team_members_list)

# ✅ Admin Authentication
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "password123":  # Change this in production
            session['admin'] = True
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        flash("Please log in as an admin.", "warning")
        return redirect(url_for('admin_login'))  # ✅ Fixed incorrect redirect
    
    return render_template('admin.html')

@app.route('/upload-team-pictures', methods=['POST'])
def upload_team_pictures():
    if 'admin' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('admin_login'))

    file = request.files.get('file')
    if file:
        file_path = os.path.join('static/uploads', file.filename)
        file.save(file_path)

        db.collection('images').document(file.filename).set({
            'url': file_path
        })
        flash("Image uploaded successfully!", "success")
    
    return redirect(url_for('admin_dashboard'))  # ✅ Fixed incorrect redirect

@app.route('/add-sponsor', methods=['POST'])
def add_sponsor():
    if 'admin' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('admin_login'))

    sponsor_name = request.form.get('sponsor_name')
    sponsor_url = request.form.get('sponsor_url')
    paypal_link = request.form.get('paypal_link')

    if sponsor_name and sponsor_url and paypal_link:
        db.collection('sponsors').document(sponsor_name).set({
            'url': sponsor_url,
            'paypal_link': paypal_link
        })
        flash("Sponsor added successfully!", "success")
    
    return redirect(url_for('admin_dashboard'))  # ✅ Fixed incorrect redirect

if __name__ == '__main__':
    app.run(debug=True)
