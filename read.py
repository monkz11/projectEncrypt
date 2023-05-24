import cv2 as cv

img = cv.imread('Photos/passport_1.jpg')

cv.imshow('passport', img)

cv.waitKey(0)
