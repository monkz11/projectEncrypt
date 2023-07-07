from flask import render_template, request
from werkzeug.utils import secure_filename
import cv2
from encrypt import app, User, db
from encrypt.passport_scan import get_scan_uri, get_mrz_data
from encrypt import database
import numpy as np
import io
from PIL import Image
import base64

# Each page on our website is accessed through a route in the form "website/route"
# For example youtube.com/home youtube.com/trending etc...
# With Flask, we must define a function that runs on each page of the website. The function determines the content
# displayed on the page.

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_passport():
    if request.method == 'POST':
        success_status = 0
        # passport_img is defined in the html file... check there for more
        file = request.files.get('passport_img')
        # If they submit with no file, just render normal page
        if (not file):
            return render_template('upload.html')
        # Allows us to read image without saving it anywhere 
        file_content = file.read()
        # Convert to numpy array, read to cv2, and find mrz
        img = np.asarray(bytearray(file_content), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        mrz_data = get_mrz_data(img) # returns dictionary w scanned image and text

        # check is data was found
        if (mrz_data is None): return render_template('upload.html', title = "Upload", success_status = -1)

        scan = mrz_data['scan']
        mrz_text = mrz_data['text']

        # Found on stackoverflow to display image without saving
        uri = get_scan_uri(scan)

        return render_template('upload.html', title = "Upload", img_uri=uri, mrz_text = mrz_text, success_status = success_status)
    return render_template('upload.html')

@app.route('/register/<mrz>', methods=['GET', 'POST'])
def register(mrz):

    if (not database.is_new_user(mrz)):
        return render_template('register.html', mrz=mrz, is_new_user=False)

    if request.method == 'POST':
        email = request.form.get('user_email')
        password = request.form.get('user_password')
        mrz_hash = database.hash_mrz(mrz)
        user = User(email=email, password=password, mrz_hash=mrz_hash)
        db.session.add(user)
        db.session.commit()
        
        for user in User.query.all():
            print(user)
        
        return f'<h1>Account created</h1>'
    return render_template('register.html', mrz=mrz, is_new_user=True)