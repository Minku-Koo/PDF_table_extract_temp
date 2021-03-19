#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-18
#

# from camelot.io import read_pdf
from camelot.utils import get_page_layout
import cv2

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
    
    return f'{x1},{y1},{x2},{y2}'


# koo fix -> imread ��� ���, �ѱ� ��� ���� ��
def hangulFilePathImageRead ( filePath ) : 
    import numpy as np
    stream = open( filePath.encode("utf-8") , "rb") 
    bytes = bytearray(stream.read()) 
    numpyArray = np.asarray(bytes, dtype=np.uint8) 
    return cv2.imdecode(numpyArray , cv2.IMREAD_UNCHANGED)
    
def get_regions_img(v, img_file):
    imgDims = cv2.imread(img_file).shape
    # koo fix
    # imgDims= hangulFilePathImageRead( img_file ).shape
    
    imageWidth = v['imageWidth']
    imageHeight = v['imageHeight']
    # koo fix
    # scalingFactorX = imgDims[0] / imageWidth
    # scalingFactorY = imgDims[1] / imageHeight
    
    scalingFactorX = imgDims[1] / imageWidth
    scalingFactorY = imgDims[0] / imageHeight
    
    
    x1 = v['x'] * scalingFactorX
    y1 = abs(v['y'] ) * scalingFactorY
    x2 = (v['x'] + v['width']) * scalingFactorX
    y2 = abs(v['y'] + v['height'] ) * scalingFactorY
    
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
    
    return f"{int(x)},{int(y)},{int(width)},{int(height)}"