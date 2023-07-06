from imutils.contours import sort_contours
import numpy as np
import pytesseract
import argparse
import imutils
import sys
import cv2
import os
from mrz.checker.td3 import TD3CodeChecker

ALPHA = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split())
FILLER_CHAR = '<'

#Rescales image, video, and live video
def rescale_frame(frame, scale=0.75):
    height = int (frame.shape[0] * scale) #scales height
    width = int (frame.shape[1] * scale) #scales width
    dimensions = (width, height) #Creates tuple for dimensions

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def scale_passport(img):
	# 500 is an arbitrary width I'm testing
	scale = 500 / img.shape[1]
	img = rescale_frame(img, scale)
	return img

def get_mrz_coords(image):
	# Opencv command converts image from its corrent format to grayscale(easier to read)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# finds the height and width of the image in (if I understand the documentation properly pixels e.g. example H=2956, W=2006)
	(H, W) = gray.shape

	#Ref for next few lines: https://pyimagesearch.com/2021/04/28/opencv-morphological-operations/
	# morph rect specifies the size of the moprhing image, and getstructingelements specifies the pixels around the central element
	rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
	sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))

	# gausian blur reduces the high freuqncy components
	gray = cv2.GaussianBlur(gray, (3, 3), 0)
	# blackhat operation finds dark regions on a light background
	blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
	cv2.imshow("Blackhat", blackhat)

	# Ref: https://pyimagesearch.com/2021/05/12/image-gradients-with-opencv-sobel-and-scharr/
	# compute the Scharr gradient of the blackhat image and scale the
	# result into the range [0, 255]

	gradient = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1) #compute Scharr edge approx
	gradient = np.absolute(gradient) #Get absolute value of matrix (since some values may be negative)
	(minVal, maxVal) = (np.min(gradient), np.max(gradient)) #returns min and max of gradient array

	# Each pixel value must fall in [0,255], so we must rescale after computing gradient. We do this using the min/max scaling method.
	gradient = (gradient - minVal) / (maxVal - minVal) # Scale elements in matrix using (pixel - min) / (max - min). Forces values into [0,1]
	gradient = (gradient * 255).astype("uint8") # Multiply by 255, placing values into [0,255]
	# cv2.imshow("Gradient", gradient) # Display image

	# apply a closing operation using the rectangular kernel to close
	# gaps in between letters -- then apply Otsu's thresholding method
	# this code closes the regions of the passport image into rectangles, higlighting the MRZ into 2 rectangles
	gradient = cv2.morphologyEx(gradient, cv2.MORPH_CLOSE, rectKernel)
	threshold = cv2.threshold(gradient, 0, 255,
		cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	# cv2.imshow("Rect Close", threshold)

	# perform another closing operation, this time using the square
	# kernel to close gaps between lines of the MRZ, then perform a
	# series of erosions to break apart connected components
	# this code closes the regions of the passport image into rectangles, higlighting the MRZ into 1 rectangle
	threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, sqKernel)
	threshold = cv2.erode(threshold, None, iterations=3)
	# cv2.imshow("Square Close", threshold)

	# cv2.waitKey(0)

	# find contours in the thresholded image and sort them from bottom
	# to top (since the MRZ will always be at the bottom of the passport)
	contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)
	contours = sort_contours(contours, method="bottom-to-top")[0]
	# initialize the bounding box associated with the MRZ
	contourMatch = []

	# loop over the contours
	for c in contours:
		# compute the bounding box of the contour and then derive the
		# how much of the image the bounding box occupies in terms of
		# both width and height
		(x, y, w, h) = cv2.boundingRect(c)
		percentWidth = w / float(W)
		percentHeight = h / float(H)
		# if the bounding box occupies > 70% width and > 2% height of the
		# image, then assume we have found the MRZ
		if percentWidth > 0.7 and percentHeight > 0.02:
			contourMatch.append((x, y, w, h))

	# if the MRZ was not found, exit the script
	if contourMatch == []:
		return None
	# pad the bounding box since we applied erosions and now need to
	# re-grow it
	i = 0
	for matches in contourMatch:
		(x, y, w, h) = matches
		pX = int((x + w) * 0.03)
		pY = int((y + h) * 0.03)
		(x, y) = (x - pX, y - pY)
		(w, h) = (w + (pX * 2), h + (pY * 2))
		# extract the padded MRZ from the image
		mrz = image[y:y + h, x:x + w]
		cv2.rectangle(image, (x,y),(x+w, y+h),(0,255,0),2)
		cv2.imshow(f'{i}', image)
		mrzWord = get_mrz_text(mrz)
		if not mrzWord: continue
		print('printing MRZ text')
		print(mrzWord)
		print(f'first letter is {mrzWord[0]}')
		# if the first word in out extracted text is P then we know its the right one
		if mrzWord[0] == 'P' and '<' in mrzWord:
			# print('returning')
			# print(is_valid_mrz_text(mrzWord))
			return (x,y,w,h)
			# return mrzWord
		i+=1
	
	return None



# def is_valid_mrz_text(mrz_text):
# 	lines = [line for line in mrz_text.split('\n') if len(line) == 44]
# 	if (len(lines) != 2): return False
# 	mrz = lines.join('\n')
# 	checker = TD3CodeChecker(mrz_string=mrz, check_expiry=False)
# 	return checker

def get_mrz_text(mrz):
	# OCR the MRZ region of interest using Tesseract, removing any
	# occurrences of spaces
	tessdata_dir_config = r'--tessdata-dir "C:/Program Files/Tesseract-OCR/tessdata"'
	mrzText = pytesseract.image_to_string(mrz,lang='mrz',config=tessdata_dir_config)
	mrzText = mrzText.replace(" ", "")
	return mrzText

def get_mrz_image(img):
	mrz_coords = get_mrz_coords(img)
	if (mrz_coords == None): return None
	(x,y,w,h) = mrz_coords
	mrz = img[y:y + h, x:x + w]
	return mrz

def get_all_scans(directory):

	scans = []
	for filename in os.listdir(directory):
		path = os.path.join(directory, filename)
		image = cv2.imread(path)
		mrz_coords = get_mrz_coords(image)
		if (mrz_coords == None): continue
		(x,y,w,h) = mrz_coords
		mrz = image[y:y + h, x:x + w]
		mrz_text = get_mrz_text(mrz)
		#print(mrz)
		#mrzText = get_mrz_text(mrz)
		scans.append(mrz_text)

	return scans


def show_scans(scans):
	print("------------ Beginning Scan")
	scanNum = 1
	for mrz in scans:
		print(f"------------ Showing scan #{str(scanNum)}")
		print(mrz)
		#cv2.imshow(mrz, scans[mrz])
		input("------------ Press any key to see next scan")
		# cv2.waitKey(0)
		scanNum += 1

	print("------------ All scans have been displayed")

def draw_mrz_rectangle(image):
	coords = get_mrz_coords(image)
	if not coords:
		return None
	x,y,w,h = get_mrz_coords(image)
	return cv2.rectangle(image, (x,y),(x+w, y+h),(0,255,0),2)

# img = cv2.imread('encrypt/static/Passports/china.jpg')
# img = draw_mrz_rectangle(img)
# if img is not None:
# 	cv2.imshow('img', img)

# cv2.waitKey(0)
