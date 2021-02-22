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
        self.p0, self.p1 = regions[0], regions[1] # line regions
        self.image = cv2.imread(self.filename) # get png file
        self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # image to gray
        self.block_size = block_size
        self.c = c
        self.line_scale = 120
        
        h, v = self.get_size()
    
    def getThreshold(self, image_gray):
        threshold = cv2.adaptiveThreshold(
                        np.invert(image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        self.block_size, # 블록 사이즈 
                        self.c # 가감 상수
                    )
        return threshold
        
    def get_size(self):
        threshold = self.getThreshold(self.image_gray)
        
        print("좌표::",self.p0,"/",self.p1)
        horizontal_size = self.calc_line_size(threshold, "h")
        threshold = self.vertical_to_horizontal(threshold)
        
        print("좌표::",self.p0,"/",self.p1)
        vertical_size = self.calc_line_size(threshold, "v")
        
        """
        1. horizontal -> calc_line_size
        2. vertical -> calc_line_size
        return value h and v
        """
        
        print("\n\n\nfinal")
        print("horizontal_size:",horizontal_size)
        print("vertical_size:",vertical_size)
        
        
        return 1, 1
    
    # 반시계 방향으로 돌려줌, 세로선 to 가로선
    def vertical_to_horizontal(self, threshold):
        convert = []
        for i in range(threshold.shape[1]):
            temp=[]
            for th in threshold:
                temp.append(th[i])
            convert.append(temp)
        convert = np.array(convert)
        temp = self.p0
        self.p0 = [self.p0[1], convert.shape[1]-self.p1[0]]
        self.p1 = [self.p1[1], convert.shape[1]-temp[0]]
        return convert
    
    def show_plot(self, threshold):
        resize_img = cv2.resize(threshold, (500, 500))
        cv2.imshow("show image", resize_img)
        cv2.waitKey(0)
    
    # 영역에서 라인 두께 리스트 반환
    def line_size_list(self, dict):
        if dict == {}: return []
        
        max_size = max(dict.keys())
        list_size = len(dict[max_size])
        
        tempList, temp = [], dict[max_size][0]-1
        max_thick_list = []
        for index in dict[max_size]:
            if index != temp+1:
                max_thick_list.append(len(tempList))
                tempList = [index]
            else:
                tempList.append(index)
            temp = index
        max_thick_list.append(len(tempList))
        print("max_thick_list",max_thick_list)
        return max_thick_list
    
    def calc_line_size(self, threshold, direction): # case horizontal
        # if direction == "h":
        size = threshold.shape[1] // self.line_scale
            
        # elif direction =="v":
            # size = threshold.shape[0] // self.line_scale
            # el = cv2.getStructuringElement(cv2.MORPH_RECT, ( 1, size))
        print(":size::",size)
        el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        self.show_plot(threshold)
        
        # set region / remove except regions
        region_mask = np.zeros(threshold.shape)
        x1, y1 = self.p0[0], self.p0[1]
        x2, y2 = self.p1[0], self.p1[1]
        region_mask[y1 : y2, x1 : x2] = 1
        threshold = np.multiply(threshold, region_mask)
        
        # opening
        threshold = cv2.erode(threshold, el) # erotion
        threshold = cv2.dilate(threshold, el) # dilation
        # dmask = cv2.dilate(threshold, el, iterations=0)
        
        self.show_plot(threshold)
        
        print("threshold.shape size:",threshold.shape)
        threshold_mark = threshold[ y1:y2, x1:x2 ]
        horizonSize = threshold_mark.shape[1]
        # np.set_printoptions(threshold=sys.maxsize)
        print("threshold_mark.shape size:",threshold_mark.shape)
        
        # key: line size / value: line index
        line_detected = {}
        index = -1
        for horizontal in threshold_mark: # one  horizontal line
            index+=1
            if horizontal[0] ==0 and horizontal[-1] ==0: continue 
            if len(set(horizontal)) == 1 : # all pixel is filled
                
                if horizonSize in line_detected.keys(): 
                    line_detected[horizonSize].append(index)
                else: line_detected[horizonSize] = [index]
                continue
            
            lineSize = 0
            temp = horizontal[0]
            for cell in enumerate(horizontal):
                if cell[1] != temp: 
                    lineSize = cell[0]+1 
                    break
            
            
            if lineSize in line_detected.keys(): 
                line_detected[lineSize].append(index)
            else: line_detected[lineSize] = [index]
        
        print("*"*20,"line detected","*"*20)
        print(line_detected)
        line_size = self.line_size_list(line_detected)
        print("\n>>>line_size:",line_size)
        
        
        
        # print("regions size:",self.regions)
        # print("threshold.shape size:",threshold.shape)
        # coord = str(w)+"-"+str(h)
        # cv2.imwrite("./-"+coord+"-t.png", threshold)
        
        print("-------"*5);print("---*----"*5);
        
        return line_size
        

if __name__ ==  "__main__":
    dirpath = "./test-photo/"
    
    imgname = "page-2"
    imgname = "line2"
    
    
    p0=[180, 360]
    p1=[230, 425]
    
    
    regions = [p0, p1]
    getlinesize = GetLineSize(dirpath+ imgname+'.png', regions)


