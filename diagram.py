import numpy as np
import cv2

# read, make it black and white
img = cv2.imread("tests/test_3_1.jpg")
# edges
canny = cv2.Canny(img, 200, 255)

# floodfill
height, width, _= img.shape

floodflags = 4
floodflags |= cv2.FLOODFILL_MASK_ONLY
floodflags |= (255 << 8)

mask = np.zeros((height+2, width+2), np.uint8)

_, _, mask, _ = cv2.floodFill(canny, mask, (0,0), (255,0,0), (10,)*3, (10,)*3, floodflags)

# erode preparations
mask = 255-mask

kernel = np.ones((3,3), np.uint8)

# erode until the arrows disappear (contour count doesn't change after erosion)

erodeIterations=0

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
prevCntLen=0
erode=mask

while prevCntLen != len(contours):
    erode = cv2.erode(erode, kernel, iterations = 1)
    
    prevCntLen = len(contours)
    contours, _ = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    erodeIterations += 1

#dilate = cv2.dilate(erode, kernel, erodeIterations)
dilate = erode
for i in range(erodeIterations):
    dilate = cv2.dilate(dilate, kernel, erodeIterations)

contours, _ = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    
    x, y, w, h = cv2.boundingRect(approx)
    cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,255), 3)
    
    cv2.putText(img, str(len(approx)), (x,y+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

#arrows = cv2.subtract(mask, dilate)

#cv2.imshow("canny", canny)
#cv2.imshow("mask", mask)

cv2.imshow("img", img)
cv2.waitKey()
cv2.destroyAllWindows()