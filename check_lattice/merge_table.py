#python
"""
# one table but camelot cannot detected. 
# it can detected tables as one, and merging
# start : 20200319
# update : 20200320
# minku Koo
"""

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
    result = []
    #  y 좌표로 오름차순 정렬
    contours = sorted(contours, key = lambda x : x[1])
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
    
    for index in range(1, max(tables.keys())+1):
        # if not continuity
        if index not in tables.keys(): 
            sameTable = []
            continue
        if index-1 not in tables.keys(): continue
        
        before_table, now_table = tables[index-1], tables[index]
        
        # kind of table check
        # 1. table - line
        if before_table[1] and now_table[1]==False:
            print("meet line")
            sameTable = [ before_table[0], now_table[0] ]
        
        # 2. line - table
        elif before_table[1]==False and now_table[1]:
            print("meet table")
            if sameTable == []:
                sameTable = [ before_table[0], now_table[0] ]
            else:
                sameTable.append( now_table[0] )
            print("sameTable", sameTable)
            result.append( sameTable )
            sameTable = []
        
        # 3. line - line
        elif before_table[1]==False and now_table[1]==False:
            print("line and line")
            if sameTable == []:
                sameTable = [ before_table[0], now_table[0] ]
            else:
                sameTable.append( now_table[0] )
            
        # 4. table - table
        else:
            # condition check
            # 1 : is same width?
            print("both table")
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
            hs_list = [[], []]  # horizontal line y coordinate list, table 1 and table 2
            for hs in horizontal_segments:
                h_y_value = hs[1] # line y coordinate
                y_value = before_table[0][1] # table 1 y coordinate
                if y_value <= h_y_value <= y_value + before_table[0][-1] :
                    hs_list[0].append( h_y_value )
                y_value = now_table[0][1] # table 2 y coordinate
                if y_value <= h_y_value <= y_value + now_table[0][-1] :
                    hs_list[1].append( h_y_value )
            
            
            top_value = before_table[0][1] + before_table[0][-1]
            bottom_value = now_table[0][1]
            # this is avertage
            # row_value1 = sum([hs_list[0][x-1] - hs_list[0][x] for x in range(1, len(hs_list[0]))]) / (len(hs_list[0])-1)
            # row_value2 = sum([hs_list[1][x-1] - hs_list[1][x] for x in range(1, len(hs_list[1]))]) / (len(hs_list[1])-1)
            # this is minimum value
            row_value1 = min([hs_list[0][x-1] - hs_list[0][x] for x in range(1, len(hs_list[0]))]) 
            row_value2 = min([hs_list[1][x-1] - hs_list[1][x] for x in range(1, len(hs_list[1]))]) 
            # 이부분 수정할 것, table + table  merge
            row_value = min( row_value1, row_value2 )
            table_by_table = bottom_value - top_value
            print("row_value1",row_value1)
            print("row_value2",row_value2)
            print("bottom_value",bottom_value)
            print("top_value",top_value)
            print("table_by_table",table_by_table)
            print("row_value",row_value)
            
            if table_by_table > row_value:
                print("no table , continue")
                continue
            else:
                sameTable.extend( [ before_table[0], now_table[0] ] )
            
            result.append( sameTable )
            sameTable = []
            
        print(">>result", result)
    return result
    
# add virture vertical line on merge table
def addVerticalLine(vertical_mask, merge_table, size=2):
    """
    Parameters
        vertical_mask <nd.array> : vertical line threshold
        merge_table <tuple in list> : Tables that require merging
        size <int> : line size
    
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
        vertical_mask[y_value1 : y_value2+size, x_value1-size : x_value1+size] = 255
        vertical_mask[y_value1 : y_value2+size, x_value2-size : x_value2+size] = 255

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
    
    contours = find_contours(vertical_mask, horizontal_mask)
    
    '''

