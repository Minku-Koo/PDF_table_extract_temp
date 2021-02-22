

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

dirpath = "./test-photo/"

imgname = "test1"
imgname = "page-2"
imgname = "page-1-crop"
imgname = "line2"

image = cv2.imread(dirpath+imgname+'.png')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
threshold = cv2.adaptiveThreshold(
                        np.invert(image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        15, # 블록 사이즈 
                        0 # 가감 상수
                    )
# size = threshold.shape[1] // 50
# el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
# size = threshold.shape[1] // 120
# el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
# threshold = cv2.erode(threshold, el)
# threshold = cv2.dilate(threshold, el)

print(">>")
index = 374
for th in threshold[374:377]:
    print(index,"/",th[418:420])
    index+=1

plt.imshow(threshold)
# plt.imshow(cv2.cvtColor(threshold, cv2.COLOR_BGR2RGB))
plt.show()
