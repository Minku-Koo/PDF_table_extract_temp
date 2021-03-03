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

def show_plot( threshold):
    # resize_img = cv2.resize(threshold, (500, 900))
    plt.imshow(threshold)
    plt.show()

dirpath = "./test-photo/"

imgname = "page-2"
# imgname = "short"
imgname = "border"
imgname = "split"

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
show_plot( threshold)

a = [520, 750]
b = [10, 360]

#   1
a = [0, 5]
b = [410, 150]


#  table 
a = [500, 2410]
b = [1700, 2950]

#  border 
a = [5, 150]
b = [390, 300]

a = [5, 500]
b = [390, 750]

a = [5, 2]
b = [710, 699]

regions = [[a[0], a[1], b[0]-a[0], b[1]-a[1]]]
# regions = [[a[0],  b[0],a[1], b[1]]]
line_scale=15
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
print("contours::",contours)

# if table has no outside border
# function make virtual border line
def make_border(direction, mask, contours):
    line_size = 2
    for c in contours:
        x, y, w, h = c
        print("this is c:",c)
        if direction=="v":
            mask[ y : y+h ,x-line_size : x+line_size ]= 255 # v
            mask[ y : y+h ,x+w-line_size : x+w+line_size ]= 255 # v
        elif direction=="h":
            mask[ y+h-line_size : y+h+line_size, x : x+w ]= 255 #h
            mask[ y-line_size : y+line_size, x : x+w ]= 255 #h
    
    return mask
    
vertical_mask = addOutline("v", vertical_mask, contours)
show_plot( vertical_mask)
    
horizontal_mask = addOutline("h", horizontal_mask, contours)
show_plot( horizontal_mask)


table_bbox = find_joints(contours, vertical_mask, horizontal_mask)

print("table_bbox",table_bbox)








