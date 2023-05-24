from imutils.contours import sort_contours
import numpy as np
import pytesseract
import argparse
import imutils
import sys
import cv2

#Rescales image, video, and live video
def rescaleFrame(frame, scale=0.75):
    height = int (frame.shape[0] * scale) #scales height
    width = int (frame.shape[1] * scale) #scales width
    dimensions = (width, height) #Creates tuple for dimensions

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

# this part of the code requires an argument of the form --image to be passed in the command line
# the image is then passed in the variable args

# cv2(Opencv command reads the image path and returns the image as a numpy array)
image = cv2.imread("Passports/passport_01.png")
image = rescaleFrame(image, 0.2)
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
cv2.imshow("Original", image)
cv2.imshow("Blackhat", blackhat)

# Ref: https://pyimagesearch.com/2021/05/12/image-gradients-with-opencv-sobel-and-scharr/
# Now we use Scharr operator which allows for edge detection in the image. 
# Scharr and Sobel edge detection rely on gradient approximations to detect edges; what is a gradient?

# Gradient
# Just like any other image convolution, we have a kernel which surrounds a pixel in a defined neighbourhood. For simplicity, assume it's 3x3.
# We inspect the North, South, East, and West pixels relative to our starting pixel. If our starting pixel is I(x,y), these pixels are 
# I(x,y+1), I(x,y-1), I(x+1,y), I(x-1,y)
# We first compute the components in the vertical (G_y) and horizontal (G_x) directions by subtracting the values stored at each of these pixels.
# Ex: G_y = I(x,y+1) - I(x,y-1)
# Then, using pythagorean theorem we can compute the angle and magnitude of the gradient formed by these components.

# Sobel and Scharr methods approximate the gradient quickly using kernels, where Scharr may provide slightly more accuracy.

# compute the Scharr gradient of the blackhat image and scale the
# result into the range [0, 255]

gradient = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1) #compute Scharr edge approx
gradient = np.absolute(gradient) #Get absolute value of matrix (since some values may be negative)
(minVal, maxVal) = (np.min(gradient), np.max(gradient)) #returns min and max of gradient array

# Each pixel value must fall in [0,255], so we must rescale after computing gradient. We do this using the min/max scaling method.
gradient = (gradient - minVal) / (maxVal - minVal) # Scale elements in matrix using (pixel - min) / (max - min). Forces values into [0,1]
gradient = (gradient * 255).astype("uint8") # Multiply by 255, placing values into [0,255]
cv2.imshow("Gradient", gradient) # Display image

cv2.waitKey(0)