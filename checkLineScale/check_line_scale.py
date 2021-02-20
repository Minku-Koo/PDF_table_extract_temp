# 20210218
# check PDF line scale 
# minku Koo
# version 1.0.0

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

dirpath = "./test-photo/"
imgname = "page-2"
# imgname = "page-1-crop"

image = cv2.imread(dirpath+ imgname+'.png')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

block_size = 13
c = 0

region = [1190, 1220, 560, 280]
line_scale = 0
for i in range(1):
    thresh = cv2.adaptiveThreshold(
                        np.invert(image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        block_size, # 블록 사이즈 
                        c # 가감 상수
                        )
    
    print("threshdhold size:",thresh.shape)
    line_scale += 150
    # if vertical 
    # size = thresh.shape[0] // line_scale
    # el = cv2.getStructuringElement(cv2.MORPH_RECT, (1, size))
    # name = "v"+str(line_scale)
    # if horizontal
    size = thresh.shape[1] // line_scale
    el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1))
    name="hh"+str(line_scale)
    
    r = True#False
    if r:
        region_mask = np.zeros(thresh.shape)
        x, y, w, h = region
        region_mask[y : y + h, x : x + w] = 1
        print( "1 count:",np.count_nonzero(thresh>0) )
        thresh = np.multiply(thresh, region_mask)
        
        # print( "1 count:",np.count_nonzero(thresh>0) )

    thresh = cv2.erode(thresh, el)
    thresh = cv2.dilate(thresh, el) #오프닝
    
    try:
        _, contours, _ = cv2.findContours(
            thresh.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    except ValueError:
        # for opencv backward compatibility
        contours, _ = cv2.findContours(
            thresh.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    print(contours)
    
    image = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    # threshd = cv2.drawContours(thresh, contours, -1, (0, 255, 0), 3)
    '''
    lines = []
    liness = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        x1, x2 = x, x + w
        y1, y2 = y, y + h
        lines.append(((x1 + x2) // 2, y2, (x1 + x2) // 2, y1))
        liness.append((x1, (y1 + y2) // 2, x2, (y1 + y2) // 2))
    '''
    # print(lines)
    # print(liness)
    # cv2.imshow("line scale image", cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # j = input()
    
    t_mark = thresh[ y:y+h, x:x+w]
    # whereDefault = np.where(t_mark > 0)
    # print(whereDefault)
    np.set_printoptions(threshold=sys.maxsize)
    print(t_mark)
    
    # cv2.imshow("line scale image", thresh)# cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))
    # img = cv2.hconcat([cv2.cvtColor(image, cv2.COLOR_BGR2RGB), cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB)])
    # cv2.imshow("line scale image "+str(line_scale), cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    print(">>>",line_scale)
    # cv2.imwrite("./"+name+".png", thresh)
    cv2.waitKey(0)


