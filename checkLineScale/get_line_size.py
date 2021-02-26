'''
# get line size
# start : 20200220
# update : 20210226
# minku Koo

Line Conditions
1. 영역 벽에 선이 붙어있음
2. 영역 내에서 가장 긴 선

horizontal, vertical 구분
vertical 경우 -> horizontal 구조로 전환 후 계산
'''

import cv2
import matplotlib.pyplot as plt
import numpy as np

class GetLineSize:
    """
    Parameters
        filename <str> : PNG file path 
        regions <int in list> : coordinate on image file 
        block_size <int> : block size for cv2.adaptiveThreshold, must odd number
    
    user can get value
        line_sizes <dict>
            - key : maximum line width (horizontal, vertical)
            - value : line size(=thick) each line
        line_size <dict>
            - key : maximum line width (horizontal, vertical)
            - value : line size (Deduplication)
    """
    
    def __init__(self, filename, regions, block_size = 15):
        self.filename = filename # file path
        # x1, x2, y1, y2 
        self.p0, self.p1 = [regions[0], regions[2]], [regions[1], regions[3]]
        
        self.image = cv2.imread(self.filename) # read png file
        self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) # image to gray
        
        self.block_size = block_size # 주변 블록 사이즈
        self.div_line_scale = 150
        
        self.line_sizes = {} # 모든 line의 두께
        self.line_size = {} # line 두께 중복 제거
        
        # main 함수 자동 실행
        self.main()
        
    
    # line size 계산
    def main(self):
        threshold = self.getThreshold(self.image_gray)
        
        #가로선 두께 계산
        max_size, horizontal_size = self.calc_line_size(threshold)
        self.line_sizes[max_size] = horizontal_size
        self.line_size[max_size] = list(set(horizontal_size))
        # 회전
        threshold = self.vertical_to_horizontal(threshold)
        #세로선 두께 계산
        max_size, vertical_size = self.calc_line_size(threshold)
        self.line_sizes[max_size] = vertical_size
        self.line_size[max_size] = list(set(vertical_size))
        
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
    
    # 반시계 방향으로 돌려줌, 세로선 to 가로선
    def vertical_to_horizontal(self, threshold):
        convert = [] #회전한 threshold 초기화
        for i in range(threshold.shape[1]):
            temp=[]
            for th in threshold: temp.append(th[i])
            convert.append(temp)
        convert.reverse()
        convert = np.array(convert)
        
        # 좌표값 변경 / 반시계방향 90도 회전
        temp = self.p0
        self.p0 = [self.p0[1], convert.shape[0]-self.p1[0]]
        self.p1 = [self.p1[1], convert.shape[0]-temp[0]]
        return convert
    
    # 영역에서 라인 두께 리스트 반환
    def line_size_list(self, dict):
        # 아무 선 감지 안된 경우
        if dict == {}: return -1, []
        
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
        # line 길이 최대값, line 두께 리스트 반환
        return max_size, size_list
    
    def calc_line_size(self, threshold): # case horizontal
        size = threshold.shape[1] // self.div_line_scale
        el = cv2.getStructuringElement(cv2.MORPH_RECT, ( size, 1 ))
        
        # set region / remove except regions
        region_mask = np.zeros(threshold.shape)
        x1, y1 = self.p0[0], self.p0[1]
        x2, y2 = self.p1[0], self.p1[1]
        region_mask[y1-1 : y2, x1-1 : x2] = 1
        threshold = np.multiply(threshold, region_mask)
        
        # opening / 모폴로지 연산
        threshold = cv2.erode(threshold, el) # erosion
        threshold = cv2.dilate(threshold, el) # dilation
        
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
            
            # 테이블 꼭지점 부분에서 line 계산
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
    print("I AM GET_LINE_SIZE MAIN")
    '''
    # How to use?
    dirpath = "./test-photo/"
    imgname = "page-2"
    
    p0=[1500, 2500]
    p1=[1700, 2680]
    
    regions = [p0[0],p1[0], p0[1],p1[1]]
    
    getlinesize = GetLineSize(dirpath+imgname+'.png', regions)
    print(getlinesize.line_size)
    print(getlinesize.line_sizes)
    '''


