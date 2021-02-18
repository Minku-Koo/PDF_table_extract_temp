# 20210218
# check PDF line scale 
# minku Koo
# version 1.0.0

import cv2
import matplotlib.pyplot as plt
import numpy as np

dirpath = "./test-photo/"
imgname = "test1"
imgname = "page-1-crop"

image = cv2.imread(dirpath+ imgname+'.png')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

block_size = 9
c = 0
thresh = cv2.adaptiveThreshold(
                        np.invert(image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        block_size, # 블록 사이즈 
                        c # 가감 상수
                        )

contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
print(contours)
image = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

cv2.imshow("line scale image", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
cv2.waitKey(0)


