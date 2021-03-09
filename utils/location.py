#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-09
#

# from camelot.io import read_pdf
from camelot.utils import get_page_layout

def get_file_dim(filepath):
    layout, dimensions = get_page_layout(filepath)
    return list(dimensions)

def get_regions(v, page_file):
    fileDims = get_file_dim(page_file)
    
    imageWidth = v['imageWidth']
    imageHeight = v['imageHeight']
    scalingFactorX = fileDims[0] / imageWidth
    scalingFactorY = fileDims[1] / imageHeight
    
    x1 = v['x'] * scalingFactorX
    y1 = abs(v['y'] - imageHeight) * scalingFactorY
    x2 = (v['x'] + v['width']) * scalingFactorX
    y2 = abs(v['y'] + v['height'] - imageHeight) * scalingFactorY
    
    # return f'{min(x1, x2)},{min(y1, y2)},{max(x1, x2)},{max(y1, y2)}'
    
    return f'{x1},{y1},{x2},{y2}'
    
def bbox_to_areas(v, bbox, page_file):
    fileDims = get_file_dim(page_file)
    
    imageWidth = v['imageWidth']
    imageHeight = v['imageHeight']
    scalingFactorX = fileDims[0] / imageWidth
    scalingFactorY = fileDims[1] / imageHeight
    
    x = bbox[0] / scalingFactorX
    y = abs(imageHeight - bbox[1]/ scalingFactorY)
    width = bbox[2] / scalingFactorX - x
    height = abs( imageHeight - bbox[3] / scalingFactorY - y )
    y -= height
    
    return f'{x},{y},{width},{height}'