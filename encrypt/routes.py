from flask import render_template, request
from werkzeug.utils import secure_filename
import cv2
import os
from encrypt import app
from encrypt.passport_scan import drawMRZRectangle

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
    # Checks if we tried to upload something
    if request.method == 'POST':
        # passport_img is defined in the html file... check there for more
        file = request.files['passport_img']
        # function that cleans up filename. eg. "my file name" becomes "my_file_name"
        filename = secure_filename(file.filename)  
        upload_path = os.path.join('encrypt/static/uploads', filename)
        scan_path = os.path.join('encrypt/static/scans', filename)
        file.save(upload_path)
        scan = drawMRZRectangle(cv2.imread(upload_path))
        cv2.imwrite(scan_path, scan)
        # Displays uploaded image on the page
        return render_template('upload.html', title = "Upload", complete_scan=os.path.join('static/scans', filename))
    # If nothing uploaded, render html without image
    return render_template('upload.html')