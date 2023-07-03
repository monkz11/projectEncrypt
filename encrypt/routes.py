from flask import render_template, request
from werkzeug.utils import secure_filename
import cv2
import os
from encrypt import app
from encrypt.passport_scan import drawMRZRectangle, getMRZCoords, getMRZText
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
        # Runs following branch if image is uploaded
        if request.form.get('submit-button') == "img":
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
            # Get coords for mrz. If it fails, return type is None
            try:
                x,y,w,h = getMRZCoords(img)
            except:
                success_status = -1
                return render_template('upload.html', title = "Upload", success_status = success_status)
            success_status = 0
            # If no failure, display the image
            scan = cv2.rectangle(img, (x,y),(x+w, y+h),(0,255,0),2)
            mrz = img[y:y + h, x:x + w]
            mrz_text = getMRZText(mrz)
            # Need to swap to RGB since cv2 uses BGR instead. If this is deleted, image colours r fucked
            scan = cv2.cvtColor(scan, cv2.COLOR_BGR2RGB)
            # Found on stackoverflow to display image without saving
            img = Image.fromarray(scan.astype("uint8"))
            rawBytes = io.BytesIO()
            img.save(rawBytes, "JPEG")
            rawBytes.seek(0)
            img_base64 = base64.b64encode(rawBytes.getvalue()).decode('ascii')
            mime = "image/jpeg"
            uri = f"data:{mime};base64,{img_base64}"
            return render_template('upload.html', title = "Upload", img_uri=uri, mrz_text = mrz_text, success_status = success_status)
        if request.form.get('submit-button') == "mrz-text":
            text = request.form.get('mrz-text')
            print(text)
            # TODO: Encrypt MRZ and add to DB
            return f"<h1>Your data has been submitted!</h1>"
    return render_template('upload.html')