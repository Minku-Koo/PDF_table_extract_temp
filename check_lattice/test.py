

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
def show_plot( threshold, title):
        resize_img = cv2.resize(threshold, (500, 500))
        # cv2.imshow("show image :"+title, resize_img)
        # cv2.waitKey(0)
        out = threshold.copy() 
        out = 255 - out

        plt.imshow(out)
        # cv2.imwrite('./h2-'+title+'.png', out)
        plt.show()

def pprint(threshold, a, b, x, y):
    index = a
    for th in threshold[a:b]:
        print(index,"/",th[x:y])
        index+=1
    # print("**"*20)
    # print("**"*20)

dirpath = "./test-photo/"

imgname = "page-2"
# imgname = "short"
imgname = "border"
imgname = "split"
# imgname = "123"
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


z,x,c,v = 180, 185, 380, 386

show_plot( threshold, "org")
pprint(threshold, z,x,c,v )

linescale = 18

# size = threshold.shape[1] // linescale
# el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))

size = threshold.shape[0] // linescale
el = cv2.getStructuringElement(cv2.MORPH_RECT, ( 1, size ))


# size = 20#size
print("size",size)
print("threshold",threshold.shape)

threshold = cv2.erode(threshold, el) # erosion
# show_plot( threshold, "after erosion")
print("-"*30,"After erosion","-"*30)
pprint(threshold, z,x,c,v )

threshold = cv2.dilate(threshold, el) # dilation
show_plot( threshold, "after dilate")
print("-"*30,"After dilate","-"*30)
pprint(threshold, z,x,c,v )

# plt.imshow(threshold)
# plt.imshow(cv2.cvtColor(threshold, cv2.COLOR_BGR2RGB))
# plt.show()
