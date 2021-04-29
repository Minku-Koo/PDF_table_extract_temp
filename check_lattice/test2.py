#python
import os
import sys
import copy
import locale
import logging
import warnings
import subprocess

import numpy as np
import pandas as pd

from merge_table import addVerticalLine, tableMerge
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys

from image_processing import (
    adaptive_threshold,
    find_lines,
    find_contours,
    find_joints,
)

from make_border import addOutline

def show_plot(title, threshold):
    # resize_img = cv2.resize(threshold, (500, 900))
    out = threshold.copy()
    out = 255 - out
    plt.imshow(out)
    # plt.imshow(threshold)
    plt.savefig("./lib-test/saver/"+title+'-dott-test.png', dpi=400)
    plt.show()

dirpath = "./lib-test/photo/"

# imgname = "page-2"
# imgname = "short"
# imgname = "border"
imgname = "dott"

def hello(dirpath):
    
    # for img in range(1, 30):
    for img in [12, 13, 16, 20, 21, 22]:
        imgname = str(img)
        print("name:",dirpath+imgname)
        imagename = dirpath+imgname+".png"
        process_background = False
        threshold_blocksize = 15
        threshold_constant = 0

        image, threshold = adaptive_threshold(
                imagename,
                process_background=process_background,
                blocksize=threshold_blocksize,
                c=threshold_constant,
            )
            
        regions = None
        line_scale= 50
        iterations = 0

        vertical_mask, vertical_segments = find_lines(
            threshold,
            regions=regions,
            direction="vertical",
            line_scale=line_scale,
            iterations=iterations,
        )

        horizontal_mask, horizontal_segments = find_lines(
            threshold,
            regions=regions,
            direction="horizontal",
            line_scale=line_scale,
            iterations=iterations,
        )

        contours = find_contours(vertical_mask, horizontal_mask)
        
        vertical_mask = addOutline("v", vertical_mask, contours)

        horizontal_mask = addOutline("h", horizontal_mask, contours)
        
        contours = find_contours(vertical_mask, horizontal_mask)
        
        addVerticalList = tableMerge(contours, vertical_segments, horizontal_segments)
        vertical_mask = addVerticalLine(vertical_mask, addVerticalList)

        contours = find_contours(vertical_mask, horizontal_mask)

        # table_bbox = find_joints(contours, vertical_mask, horizontal_mask)
        show_plot(imgname+"-r",  horizontal_mask + vertical_mask)
        
        maps = horizontal_mask + vertical_mask
        map = cv2.cvtColor(maps, cv2.COLOR_GRAY2RGB)
        for cont in contours:
            x, y, w, h = cont
            value = [ 50, 255, 20 ]
            for x_ in range(x, x+w):
                map[y][x_] = value
                map[y+h][x_] = value
            for y_ in range(y, y+h):
                map[y_][x] = value
                map[y_][x+w] = value
        
        show_plot(imgname+"-table", map)
        
        
        print("============== save")
        
        

# hello(dirpath)


imagename = dirpath+imgname+".png"
process_background = False
threshold_blocksize = 15
threshold_constant = 0

image, threshold = adaptive_threshold(
            imagename,
            process_background=process_background,
            blocksize=threshold_blocksize,
            c=threshold_constant,
        )


#  border 
a = [5, 150]
b = [390, 300]

a = [5, 500]
b = [390, 750]

a = [300, 1500]
b = [2500, 3000]

regions = [[a[0], a[1], b[0]-a[0], b[1]-a[1]]]
regions = None
# regions = [[a[0],  b[0],a[1], b[1]]]
line_scale= 40
iterations = 0

vertical_mask, vertical_segments = find_lines(
    threshold,
    regions=regions,
    direction="vertical",
    line_scale=line_scale,
    iterations=iterations,
)

horizontal_mask, horizontal_segments = find_lines(
    threshold,
    regions=regions,
    direction="horizontal",
    line_scale=line_scale,
    iterations=iterations,
)


show_plot("org", vertical_mask+horizontal_mask)

        
print("original")
# show_plot(imgname+"-threshold", vertical_mask + horizontal_mask)

contours = find_contours(vertical_mask, horizontal_mask)
print("first camelot contours::",contours)

vertical_mask = addOutline("v", vertical_mask, contours)
print("after add vertical")
# show_plot( vertical_mask)

horizontal_mask = addOutline("h", horizontal_mask, contours)
print("after add horizontal")
show_plot("addOutline", vertical_mask+horizontal_mask)


contours = find_contours(vertical_mask, horizontal_mask)
print("vertical  + horizontal")
# show_plot(imgname+"-addOutline",  horizontal_mask + vertical_mask)
print("vertical  + horizontal contours::",contours)


addVerticalList = tableMerge(contours, vertical_segments, horizontal_segments)
print("addVerticalList", addVerticalList)
show_plot(imgname+"-tableMerge",  horizontal_mask + vertical_mask)
vertical_mask = addVerticalLine(vertical_mask, addVerticalList)
show_plot(imgname+"-addVerticalLine",  horizontal_mask + vertical_mask)

# get contours once again
contours = find_contours(vertical_mask, horizontal_mask)
print(">final contours:", contours)
print("this is result")
# show_plot(imgname+"-addVertical",  horizontal_mask + vertical_mask)

table_bbox = find_joints(contours, vertical_mask, horizontal_mask)

# print("table_bbox",table_bbox)












