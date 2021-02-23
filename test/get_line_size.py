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
        # x1, x2, y1, y2 
        self.p0, self.p1 = [regions[0], regions[2]], [regions[1], regions[3]]
        self.image = cv2.imread(self.filename) # read png file
        self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # image to gray
        self.block_size = block_size # 주변 블록 사이즈
        self.c = c # 가감 상수
        self.div_line_scale = 120
        
        self.line_sizes = []
        self.line_size = []
        self.line_scale = 15
        
        self.main()
        
    
    # line size 계산
    def main(self):
        threshold = self.getThreshold(self.image_gray)
        
        #가로선 두께 계산
        horizontal_size = self.calc_line_size(threshold)
        # 회전
        threshold = self.vertical_to_horizontal(threshold)
        #세로선 두께 계산
        vertical_size = self.calc_line_size(threshold)
        
        self.line_sizes = horizontal_size + vertical_size
        self.line_size = list(set(self.line_sizes))
        
        self.line_scale = 120 # function
        
        return 0
    
    # Threshold계산
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
    
    # 반시계 방향으로 돌려줌, 세로선 to 가로선
    def vertical_to_horizontal(self, threshold):
        convert = [] #회전한 threshold
        for i in range(threshold.shape[1]):
            temp=[]
            for th in threshold:
                temp.append(th[i])
            convert.append(temp)
        convert.reverse()
        convert = np.array(convert)
        
        # 좌표값 변경
        temp = self.p0
        self.p0 = [self.p0[1], convert.shape[1]-self.p1[0]]
        self.p1 = [self.p1[1], convert.shape[1]-temp[0]]
        
        return convert
    
    # 나중에 삭제할 것 > 호출한 부분도 삭제할 것
    def show_plot(self, threshold):
        resize_img = cv2.resize(threshold, (500, 500))
        # cv2.imshow("show image", resize_img)
        # cv2.waitKey(0)
        
        pass
    
    # 영역에서 라인 두께 리스트 반환
    def line_size_list(self, dict):
        # 아무 선 감지 안된 경우
        if dict == {}: return []
        
        #최대 선 길이
        max_size = max(dict.keys())
        
        # 연속된 선 리스트, 인덱스
        tempList, temp = [], dict[max_size][0]-1
        size_list = [] # 선 두께 리스트
        for index in dict[max_size]: 
            if index != temp+1: #연속되지 않은 경우
                size_list.append(len(tempList))
                tempList = [index] #선 리스트 초기화
            else: #연속된 경우
                tempList.append(index) #선 두께 추가
            temp = index
        size_list.append(len(tempList)) #마지막에 감지된 선 추가
        # print("size_list:",size_list)
        return size_list
    
    def calc_line_size(self, threshold): # case horizontal
        size = threshold.shape[1] // self.div_line_scale
        el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        self.show_plot(threshold)
        
        # set region / remove except regions
        region_mask = np.zeros(threshold.shape)
        x1, y1 = self.p0[0], self.p0[1]
        x2, y2 = self.p1[0], self.p1[1]
        region_mask[y1 : y2, x1 : x2] = 1
        threshold = np.multiply(threshold, region_mask)
        
        # opening
        threshold = cv2.erode(threshold, el) # erosion
        threshold = cv2.dilate(threshold, el) # dilation
        
        try:
            _, contours, _ = cv2.findContours(
                threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        except ValueError:
            # for opencv backward compatibility
            contours, _ = cv2.findContours(
                threshold.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        
        for c in contours:
            # print("c>",cv2.boundingRect(c))
            pass
        
        
        self.show_plot(threshold)
        
        threshold_mark = threshold[ y1:y2, x1:x2 ]
        horizonSize = threshold_mark.shape[1] # 영역 가로 픽셀값
        
        # key: line size / value: line index
        line_detected = {} # 감지된 line 저장
        index = -1 # 세로 인덱스(per pixel) , for문 처음에 1 추가하면서 시작하기 때문에 -1로 설정
        for horizontal in threshold_mark: # one  horizontal line
            index+=1
            # 양 사이드 모두 0일 경우 = line으로 볼 수 없음
            if horizontal[0] ==0 and horizontal[-1] ==0: continue 
            # 모든 픽셀값이 1개일 경우=모든 픽셀에 0이상 값 존재 / all pixel is filled
            # (모두 0일 경우는 위에서 걸러짐)
            if len(set(horizontal)) == 1 :
                if horizonSize in line_detected.keys(): 
                    line_detected[horizonSize].append(index)
                else: line_detected[horizonSize] = [index]
                continue
            
            lineSize = 0 # line size 초기화
            temp = horizontal[0] # 초기값은 0번째 index로 설정 (비교 위해)
            for cell in enumerate(horizontal):
                if cell[1] != temp: 
                    lineSize = cell[0]+1 
                    break
            
            # 계산된 line width와line index를 저장
            if lineSize in line_detected.keys(): 
                line_detected[lineSize].append(index)
            else: line_detected[lineSize] = [index]

        # line size 계산하고 반환
        return self.line_size_list(line_detected)
    

if __name__ ==  "__main__":
    dirpath = "./test-photo/"
    
    imgname = "page-2"
    imgname = "line2"
    
    
    p0=[360, 210]
    p1=[420, 333]
    
    p0=[333, 400]
    p1=[420, 550]
    
    regions = [p0[0],p1[0], p0[1],p1[1]]
    
    getlinesize = GetLineSize(dirpath+ imgname+'.png', regions)
    print("**--- after class ---")
    print(getlinesize.line_size)
    print(getlinesize.line_sizes)
    print(getlinesize.line_scale)


