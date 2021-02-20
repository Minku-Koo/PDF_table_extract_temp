# get line size
# 20200220
# minku Koo

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

'''
라인 조건
1. 영역 벽에 붙어있음
2. 가장 긴 선

horizontal, vertical 구분
vertical 경우 -> horizontal 구조로 전환 후 계산

'''


class GetLineSize:
    def __init__(self, filename, regions, block_size = 15, c=0):
        self.filename = filename # file path
        self.regions = regions # line regions
        self.image = cv2.imread(self.filename) # get png file
        self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # image to gray
        self.block_size = block_size
        self.c = c
        self.line_scale = 20
        
        h, v = self.get_size()
    
    def get_size(self):
        threshold = cv2.adaptiveThreshold(
                        np.invert(self.image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        self.block_size, # 블록 사이즈 
                        self.c # 가감 상수
                    )
        
        h = self.calc_line_size(threshold)
        """
        1. horizontal -> calc_line_size
        2. vertical -> calc_line_size
        return value h and v
        """
        return 1, 1
    
    def vertical_to_horizontal(self, threshold):
        pass
        return threshold
    
    def calc_line_size(self, threshold): # case horizontal
        size = threshold.shape[1] // self.line_scale
        el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        
        resize_img = cv2.resize(threshold, (500, 500))
        cv2.imshow("erotion", resize_img)
        cv2.waitKey(0)
        # set region / remove except regions
        region_mask = np.zeros(threshold.shape)
        x, y, w, h = self.regions
        region_mask[y : y + h, x : x + w] = 1
        threshold = np.multiply(threshold, region_mask)
        
        
        # opening
        threshold = cv2.erode(threshold, el) # erotion
        """
        resize_img = cv2.resize(threshold, (500, 500))
        cv2.imshow("erotion", resize_img)
        cv2.waitKey(0)
        """
        threshold = cv2.dilate(threshold, el) # dilation
        # dmask = cv2.dilate(threshold, el, iterations=0)
        # print(threshold)
        resize_img = cv2.resize(threshold, (500, 500))
        cv2.imshow("dilation", resize_img)
        cv2.waitKey(0)
        """
        print(">> after dilation")
        fuck_list = []
        for horizontal in threshold[crop_a: crop_b ]: # one  horizontal line
            # index+=1
            print(horizontal[h_a:h_b])
            fuck_list.append(set(horizontal))
        # print(fuck_list)
        print(fuck_list)
        print("//")
        i=0
        for f in fuck_list:
            if max(list(f)) >0: print(i, end="/")
            i+=1
        # np.savetxt('test3.txt', threshold, fmt = '%2d', delimiter = ',', header='test3',newline='\n\n')  
        """
            
        print("threshold.shape size:",threshold.shape)
        threshold_mark = threshold[ y:y+h, x:x+w]
        REGION_HORIZONTAL = threshold_mark.shape[1]
        np.set_printoptions(threshold=sys.maxsize)
        # print(threshold_mark)
        print("threshold_mark.shape size:",threshold_mark.shape)
        resize_img = cv2.resize(threshold_mark, (500, 500))
        cv2.imshow("crop", resize_img)
        cv2.waitKey(0)
        
        """
        lines=[]
        print(contours)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            x1, x2 = x, x + w
            y1, y2 = y, y + h
            lines.append((x1, (y1 + y2) // 2, x2, (y1 + y2) // 2))
        print(lines)
        cv2.imwrite("./-66-t.png", threshold)
        """
        size_list = []
        index_list = []
        index = -1
        for horizontal in threshold_mark: # one  horizontal line
            index+=1
            if horizontal[0] ==0 and horizontal[-1] ==0: continue 
            if len(set(horizontal)) == 1 : # all pixel is filled
                size_list.append(REGION_HORIZONTAL)
                index_list.append(index)
                print("set")
                continue
            
            count = 0
            print("**"*20)
            for left, right in zip(horizontal, reversed(horizontal)):
                # print(left,'/index',index,'/',right)
                if (left==0 and right==0) or (left!=0 and right!=0): break
                
                count +=1
                # print("c:",count)
            print("count")
            size_list.append(count)
            index_list.append(index)
            '''
            max_value, count = [], 0
            for pixel in horizontal: # one pixel
                if pixel !=0 : count +=1
                else:
                    max_value.append(count)
                    count =0 
            
            size_list.append(max(max_value))
            '''
        
        # for horizontal in threshold[780:780+800]: print(horizontal[207:207+200])
        
        print("index",index)
        print("*"*20," size list ",'-'*20)
        print(size_list)
        print("*"*20," index list ",'-'*20)
        print(index_list)
        print("-------"*5)
        print("regions size:",self.regions)
        print("threshold.shape size:",threshold.shape)
        # print(fuck_list)
        coord = str(w)+"-"+str(h)
        cv2.imwrite("./-"+coord+"-t.png", threshold)
        
        return 0
        

if __name__ ==  "__main__":
    dirpath = "./test-photo/"
    
    imgname = "page-1-crop"
    imgname = "test1"
    imgname = "page-2"
    imgname = "line2"
    regions =  [1190, 1220, 560, 280]
    p0 = (207, 780)
    p1 = (257, 844)
    
    p0=(1658, 1395)
    p1=( 1774, 1478)
    
    p0=(520, 60)
    p1=(530, 75)
    
    p0=(600, 2820)
    p1=(610, 2830)
    
    p0=(310//3, 80*2)
    p1=(325//2, 85*5)
    
    p0=(711, 360)
    p1=(766, 440)
    
    # p0 = (0, 0)
    # p1 = (2000, 3000)
    regions = [p0[0], p0[1], p1[0]-p0[0], p1[1]-p0[1]]
    
    getlinesize = GetLineSize(dirpath+ imgname+'.png', regions)


