from imutils.contours import sort_contours
import numpy as np
import pytesseract
import argparse
import imutils
import sys
import cv2
import os

# Uncomment for jicky to make tesseract work
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

#Rescales image, video, and live video
def rescaleFrame(frame, scale=0.75):
    height = int (frame.shape[0] * scale) #scales height
    width = int (frame.shape[1] * scale) #scales width
    dimensions = (width, height) #Creates tuple for dimensions

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


def getMRZ(image):
	# 600 is an arbitrary width I'm testing
	scale = 600 / image.shape[1]
	image = rescaleFrame(image, scale)
	# Opencv command converts image from its corrent format to grayscale(easier to read)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# finds the height and width of the image in (if I understand the documentation properly pixels e.g. example H=2956, W=2006)
	(H, W) = gray.shape

	#Ref for next few lines: https://pyimagesearch.com/2021/04/28/opencv-morphological-operations/
	# morph rect specifies the size of the moprhing image, and getstructingelements specifies the pixels around the central element
	rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
	sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

	# gausian blur reduces the high freuqncy components
	gray = cv2.GaussianBlur(gray, (3, 3), 0)
	# blackhat operation finds dark regions on a light background
	blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
	# cv2.imshow("Blackhat", blackhat)

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
	#cv2.imshow("Rect Close", threshold)

	# perform another closing operation, this time using the square
	# kernel to close gaps between lines of the MRZ, then perform a
	# series of erosions to break apart connected components
	# this code closes the regions of the passport image into rectangles, higlighting the MRZ into 1 rectangle
	threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, sqKernel)
	threshold = cv2.erode(threshold, None, iterations=2)
	#cv2.imshow("Square Close", threshold)

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
	for matches in contourMatch:
		(x, y, w, h) = matches
		pX = int((x + w) * 0.03)
		pY = int((y + h) * 0.03)
		(x, y) = (x - pX, y - pY)
		(w, h) = (w + (pX * 2), h + (pY * 2))
		# extract the padded MRZ from the image
		mrz = image[y:y + h, x:x + w]
		mrzWord = getMRZText(mrz)
		# if the first word in out extracted text is P then we know its the right one
		if mrzWord[0] == 'P':
			return mrzWord
	
	return None

def getMRZText(mrz):
	# OCR the MRZ region of interest using Tesseract, removing any
	# occurrences of spaces
	mrzText = pytesseract.image_to_string(mrz)
	mrzText = mrzText.replace(" ", "")
	return mrzText


def getAllScans(directory):

	scans = []
	for filename in os.listdir(directory):
		path = os.path.join(directory, filename)
		image = cv2.imread(path)
		mrz = getMRZ(image)
		#print(mrz)
		#mrzText = getMRZText(mrz)
		scans.append(mrz)

	return scans


def showScans(scans):
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
	

showScans(getAllScans("./Passports"))
