
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import firestore, storage
import os

app = Flask(__name__)

# Firestore setup
db = firestore.Client(project='jag-wire-robotic')

# Cloud Storage setup
storage_client = storage.Client()
bucket_name = "jag_wire_robotic_website"
bucket = storage_client.bucket(bucket_name)

@app.route('/')
def home():
    social_links = db.collection('social_links').stream()
    links = {link.id: link.to_dict() for link in social_links}
    return render_template('index.html', social_links=links)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)
            db.collection('images').add({
                'file_name': file.filename,
                'url': blob.public_url
            })
            return redirect(url_for('upload'))
    images = db.collection('images').stream()
    image_data = [{'file_name': img.id, **img.to_dict()} for img in images]
    return render_template('upload.html', images=image_data)

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
