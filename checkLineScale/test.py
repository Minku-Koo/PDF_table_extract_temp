

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
def show_plot( threshold, title):
        resize_img = cv2.resize(threshold, (500, 500))
        # cv2.imshow("show image :"+title, resize_img)
        # cv2.waitKey(0)
        plt.imshow(threshold)
        plt.show()

def pprint(threshold, a, b, x, y):
    index = a
    for th in threshold[a:b]:
        print(index,"/",th[x:y])
        index+=1
    print("**"*20)
    print("**"*20)

dirpath = "./test-photo/"

imgname = "erosion"

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


show_plot( threshold, "threshold")
pprint(threshold, 20, 50, 20, 60)

linescale = 30
size = threshold.shape[1] // linescale
print("size",size)
el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
threshold = cv2.erode(threshold, el) # erosion
show_plot( threshold, "after erosion")
pprint(threshold, 20, 50, 20, 60)

threshold = cv2.dilate(threshold, el) # dilation
show_plot( threshold, "after dilate")
# pprint(threshold, 20, 50, 20, 60)

# plt.imshow(threshold)
# plt.imshow(cv2.cvtColor(threshold, cv2.COLOR_BGR2RGB))
# plt.show()
