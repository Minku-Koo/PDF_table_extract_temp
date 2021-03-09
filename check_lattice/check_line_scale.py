"""
# check line scale
# start : 20200225
# update : 20210310
# minku Koo
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np

class GetLineScale:
    """
    Parameters
    ----------
        filename <str> : PNG file path 
        regions <int in list> : coordinate on image file 
        block_size <int> : block size for cv2.adaptiveThreshold, must odd number
    
    user can get value
    ----------
        line_size <tuple> : get line coordinate and width, height (x, y, w, h)
        line_scale <int> : get adapted minimum line scale value
        
        if no line detected
             line_size = [-1]
             line_scale = -1
    """
    
    def __init__(self, filename, regions, block_size = 15):
        self.filename = filename # file path
        # regions = [ x1, y1, x2, y2 ]
        self.p0, self.p1 = [regions[0], regions[1]], [regions[2], regions[3]]
        
        self.image = cv2.imread(self.filename) # read png file
        self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # image to gray
        
        self.block_size = block_size # 주변 블록 사이즈
        self.div_line_scale = 150 # line_scale value for erosion and dilation
        self.direction = "v" #  detected line direction
        self.pick_line = [] # detected line in regions
        self.line_size = [] # detected line total size (x, y, w, h)
        self.line_scale = 15 # adapted  mininum line scale (default = 15)
        
        # main 함수 자동 실행
        self.main()
        
    # line size 계산
    def main(self):
        threshold = self.getThreshold(self.image_gray)
        
        # find direction, first horizontal 
        if self.find_direction(threshold, "h"): self.direction = "h"
        # second vertical
        elif self.find_direction(threshold, "v"): pass # vertical is default, pass
        else: # no line detected
            self.line_size = [-1]
            self.line_scale = -1
            return -1
        
        self.line_size = self.calc_line_size(threshold)
        self.line_scale = self.adapted_line_scale(threshold)
        return 0
    
    # Threshold계산
    def getThreshold(self, image_gray):
        threshold = cv2.adaptiveThreshold(
                        np.invert(image_gray), 
                        255, #흑백 명도 최대값
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #평균 계산 방법 / ADAPTIVE_THRESH_MEAN_C
                        cv2.THRESH_BINARY, # 흑백 반전 여부 /THRESH_BINARY_INV
                        self.block_size, # 블록 사이즈 
                        0 # 가감 상수
                    )
        return threshold
    
    def getContours(self, threshold):
        try:
            __, contours, __ = cv2.findContours(
                threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        except ValueError:
            # for opencv backward compatibility
            contours, __ = cv2.findContours(
                threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        return contours
    
    def find_direction(self, threshold, direction):
        region_mask = np.zeros(threshold.shape)
        x1, y1 = self.p0[0], self.p0[1]
        x2, y2 = self.p1[0], self.p1[1]
        region_mask[y1 : y2, x1 : x2] = 1
        threshold = np.multiply(threshold, region_mask)
        
        if direction == "h":
            # horizontal calculation
            size = threshold.shape[1] // self.div_line_scale
            el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        elif direction == "v":
            # vertical calculation
            size = threshold.shape[0] // self.div_line_scale
            el = cv2.getStructuringElement(cv2.MORPH_RECT, ( 1, size))
        
        threshold = cv2.dilate(threshold, el) # dilation
        threshold = cv2.erode(threshold, el) # erosion
        
        threshold = cv2.erode(threshold, el) # erosion
        threshold = cv2.dilate(threshold, el) # dilation
        
        contours = self.getContours(threshold)
        for c in contours:
            c_poly = cv2.approxPolyDP(c, 3, True) #테두리 단순화
            x, y, w, h = cv2.boundingRect(c_poly) # 주어진 점들 (테두리) 감싸는 최소 사각형 면적
            self.pick_line = [x, y]
            
        threshold = np.unique(threshold) # 중복 제거
        
        # 중복 제거하고 모두 0이면 false / 0 이외 값이 있으면 (line 존재하는 것이므로) true
        if len(threshold)==1: return False
        else: return True
        
    def calc_line_size(self, threshold): # case horizontal
        if self.direction == "h":
            # horizontal calculation
            size = threshold.shape[1] // self.div_line_scale
            el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        elif self.direction == "v":
            # vertical calculation
            size = threshold.shape[0] // self.div_line_scale
            el = cv2.getStructuringElement(cv2.MORPH_RECT, ( 1, size))
        
        # closing calculation
        threshold = cv2.dilate(threshold, el) # erosion
        threshold = cv2.erode(threshold, el) # dilation
        
        # opening / 모폴로지 연산
        threshold = cv2.erode(threshold, el) # erosion
        threshold = cv2.dilate(threshold, el) # dilation
        
        contours = self.getContours( threshold)
        cont = []
        for c in contours:
            c_poly = cv2.approxPolyDP(c, 3, True) #테두리 단순화
            x, y, w, h = cv2.boundingRect(c_poly) # 주어진 점들 (테두리) 감싸는 최소 사각형 면적
            cont.append((x, y, w, h)) # 페이지 내 모든 line 추가
            
        pick_x, pick_y = self.pick_line[0] ,self.pick_line[1] 
        for line in cont:
            # 모든 line중에서 pick_line 범위를 포함하는 line 구하기
            if pick_x < line[0] or pick_x > line[0]+line[2] : continue
            if pick_y >= line[1] and pick_y <= line[1]+line[3] : return line
        
        # pick line 포함하는 line이 없는 경우
        return [-1]
        
    def adapted_line_scale(self, threshold):
        if self.line_size == [-1]: # 선택된 line이 없는 경우
            return -1
        
        if self.direction == "h": # if horizontal
            return threshold.shape[1] // self.line_size[2] +1
        elif self.direction == "v": # if vertical
            return threshold.shape[0] // self.line_size[3] +1
        
        return -1 # anyway error

if __name__ ==  "__main__":
    print("I AM CHECK_LINE_SCALE MAIN")
    '''
    # How to use?
    dirpath = "./test-photo/"
    imgname = "page-2"
    
    p0=[820, 55]
    p1=[840 , 62]
    
    regions = [p0[0],p1[0], p0[1],p1[1]]
    
    getlinescale = GetLineScale(dirpath+ imgname+'.png', regions)
    print("line size >", getlinescale.line_size)
    print("adapted line scale >", getlinescale.line_scale)
    '''
    
    