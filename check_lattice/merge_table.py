#python
"""
# one table but camelot cannot detected. 
# it can detected tables as one, and merging
# start : 20200319
# update : 20200324
# minku Koo
"""

import pandas as pd

# calculate table row value > merge or not
def __calc_row_value(horizontal_seg, before_table, now_table, table=True):
    """
    Parameters
        horizontal_seg <tuple in list> : horizontal line position
        before_table <list> : [ before table coordinate <tuple>, table or line <boolean> ]
        now_table <list> : [ now table coordinate <tuple>, table or line <boolean> ]
        table <boolean> : is table or line, table is true (default = True)
    
    returns
       boolean : True - merge / False - not merge
    """
    
    result = [[], []]
    for hs in horizontal_seg:
        h_y_value = hs[1] # line y coordinate
        h_x_value = hs[0]
        
        y_value = before_table[0][1] # table 1 y coordinate
        x_value =  before_table[0][0]
        if y_value <= h_y_value <= y_value + before_table[0][-1] \
            and x_value <= h_x_value <= x_value + before_table[0][2]:
            result[0].append( h_y_value )
            
        y_value = now_table[0][1] # table 2 y coordinate
        x_value =  now_table[0][0]
        if y_value <= h_y_value <= y_value + now_table[0][-1] \
            and x_value <= h_x_value <= x_value + now_table[0][2]:
            result[1].append( h_y_value )
    
    result[0] = sorted(result[0], reverse=True)
    result[1] = sorted(result[1], reverse=True)
    
    if len(result[0]) > 1:
        row_value1 = min([result[0][x-1] - result[0][x] for x in range(1, len(result[0]))]) 
        
        if table: # table
            if len(result[1]) > 1:
                row_value2 = min([result[1][x-1] - result[1][x] for x in range(1, len(result[1]))]) 
                row_value =  min( row_value1, row_value2 )
            else:
                row_value =  row_value1
        else: # line
            row_value =  row_value1
            
    else:
        row_value = 1
    
    top_value = before_table[0][1] + before_table[0][-1]
    bottom_value = now_table[0][1]
    table_by_table = bottom_value - top_value
    
    if table_by_table > row_value: return False # not merge
    return True # merge
    
    
#  find Tables that require merging on page
def tableMerge(contours, vertical_segments, horizontal_segments, scale = 15):
    """
    Parameters
        contours <tuple in list> : detedted table
        vertical_segments <tuple in list> : vertical line position
        horizontal_segments <tuple in list> : horizontal line position
        scale <int> : If bigger than scale value, judge by table
                      If smaller than scale value, jedge by line (default = 15)
    
    returns
        result <tuple in list> : Tables that require merging
    """
    if contours == [] : return []
    
    result = []
    #  y 좌표로 오름차순 정렬
    contours = sorted(contours, key = lambda x : (x[1], x[0]) )
    vertical_segments = sorted(vertical_segments, key = lambda x : x[-1])
    
    isTable = True # table or line
    tables = {} # detected table list / key: table index, value : [ table contours, isTable ]
    
    
    for index, table in enumerate(contours):
        isTable = True if table[-1] > scale else False
        if index == 0: 
            tables[index] = [table , isTable]
            continue
            
        if not isTable: # if not table, line
            
            #  condition 1 : is same width?
            if contours[index-1][2] != table[2]: continue
            #  condition 2 : is same x coordinate?
            if contours[index-1][0] != table[0]: continue
            
            
        tables[index] = [table , isTable]
        
    isTable = False # table or line
    sameTable = [] # this list append same table
    
    if tables == {} : return []
    
    for index in range(1, max(tables.keys())+1):
        if index not in tables.keys(): 
            sameTable = []
            continue
        if index-1 not in tables.keys(): continue
        
        before_table, now_table = tables[index-1], tables[index]
        
        # kind of table check
        # 1. table - line
        if before_table[1] and now_table[1]==False:
            if __calc_row_value(horizontal_segments, before_table, now_table, table=False) :
                sameTable = [ before_table[0], now_table[0] ]
            else:
                sameTable = []
                continue
            
        
        # 2. line - table
        elif before_table[1]==False and now_table[1]:
            
            if sameTable == []:
                sameTable = [ before_table[0], now_table[0] ]
                
            else:
                sameTable.append( now_table[0] )
            result.append( sameTable )
            sameTable = []
        
        # 3. line - line
        elif before_table[1]==False and now_table[1]==False:
            if sameTable == []:
                sameTable = [ before_table[0], now_table[0] ]
            else:
                sameTable.append( now_table[0] )
            
        # 4. table - table
        else:
            # condition check
            # 1 : is same width?
            if before_table[0][2] != now_table[0][2]: continue
            # 2 : is same x coordinate?
            if before_table[0][0] != now_table[0][0]: continue
            # 3 : Are any of the vertical axes of the two tables consistent?
            vs_list = [[], []] # vertical line x coordinate list, table 1 and table 2
            for vs in vertical_segments:
                y_value = before_table[0][1] # if line in table 1
                if y_value <= vs[1] <= y_value + before_table[0][-1] :
                    vs_list[0].append( vs[0] )
                y_value = now_table[0][1] # if line in table 2
                if y_value <= vs[1] <= y_value + now_table[0][-1] :
                    vs_list[1].append( vs[0] )
                    
            for v in vs_list[0]: # if table 1 line and table 2 line are same
                if v in vs_list[1]:
                    isTable = True 
                    break
            
            if not isTable: continue
            # 4 : check interval between tables
            
            if __calc_row_value(horizontal_segments, before_table, now_table) :
                sameTable.extend( [ before_table[0], now_table[0] ] )
                
            else:
                sameTable = []
                continue
                
            result.append( sameTable )
            sameTable = []
    
    return result
    
# add virture vertical line on merge table
def addVerticalLine(vertical_mask, merge_table, lineSize=1):
    """
    Parameters
        vertical_mask <nd.array> : vertical line threshold
        merge_table <tuple in list> : Tables that require merging
        lineSize <int> : line size <default = 1>
    
    returns
        vertical_mask <nd.array> : added vertical line on threshold
    """
    for table in merge_table:
        # set x, y value
        x_value1 = table[0][0]
        x_value2 = table[0][0] + table[0][2]
        y_value1 = table[0][1]
        y_value2 = table[-1][1]
        
        # add vertical line, left and right side
        vertical_mask[y_value1 : y_value2+lineSize, x_value1-lineSize : x_value1+lineSize] = 255
        vertical_mask[y_value1 : y_value2+lineSize, x_value2-lineSize : x_value2+lineSize] = 255

    return vertical_mask


if __name__ ==  "__main__":
    print("I AM MERGE_TABLE MAIN")
    '''
    # How to use?
    
    from merge_table import tableMerge, addVerticalLine # call module
    
    # after addOutline
    contours = find_contours(vertical_mask, horizontal_mask)
    
    addVerticalList = tableMerge(contours, vertical_segments, horizontal_segments)
    vertical_mask = addVerticalLine(vertical_mask, addVerticalList)
    
    # get contours once again
    contours = find_contours(vertical_mask, horizontal_mask)
    
    '''

