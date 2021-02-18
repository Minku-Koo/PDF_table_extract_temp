# 20210218
# check PDF line scale 
# minku Koo
# version 1.0.0

import cv2
import matplotlib.pyplot as plt

image = cv2.imread('./test-photo/test1.png')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY_INV)

contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
print(contours)
image = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

cv2.imshow("image",cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
cv2.waitKey(0)


