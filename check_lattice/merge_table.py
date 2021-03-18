#python


def tableMerge(contours, vertical_segments, horizontal_segments):
    # print("hello")
    result = []
    # y 값으로 정렬
    contours = sorted(contours, key = lambda x : x[1])
    vertical_segments = sorted(vertical_segments, key = lambda x : x[-1])
    # print("after sorted:", contours)
    # print("vertical_segments::",vertical_segments)
    scale = 10 # 테이블 아닌 선분이 테이블로 인식되는 경우, 최소 두께 (line scale로 하면 될듯)
    
    isTable = True
    tables = {} 
    for index, table in enumerate(contours):
        isTable = True if table[-1] > scale else False
        if index == 0: 
            tables[index] = [table , isTable]
            continue
            
        if not isTable: # 선분
            #  조건 1 : 넓이가 같은가
            if contours[index-1][2] != table[2]: 
                # isTable = False
                continue
            # 조건 2 : x 좌표가 동일한가
            if contours[index-1][0] != table[0]: 
                # isTable = False
                continue
        
        tables[index] = [table , isTable]
        
    isTable = False
    table_set = []
    # print("tables>>",tables)
    # print("max table",max(tables.keys())+1)
    # print("horizontal_segments",horizontal_segments)
    for index in range(1, max(tables.keys())+1):
        # 연속되지 않으면 
        if index not in tables.keys(): 
            table_set = []
            continue
        if index-1 not in tables.keys(): continue
        
        # 조건 판단
        # print("*****", end="")
        if tables[index-1][1] and tables[index][1]==False:
            # print("meet line")
            table_set = [ tables[index-1][0], tables[index][0] ]
        
        elif tables[index-1][1]==False and tables[index][1]:
            # print("meet table")
            table_set.append( tables[index][0] )
            result.append( table_set )
            table_set = []
        
        elif tables[index-1][1]==False and tables[index][1]==False:
            # print("line and line")
            table_set.append( tables[index][0] )
        
        else: # true true
            #  조건 1 : 넓이가 같은가
            # print("both table")
            if tables[index-1][0][2] != tables[index][0][2]: continue
            # 조건 2 : x 좌표가 동일한가
            if tables[index-1][0][0] != tables[index][0][0]: continue
            # 조건 3 : 테이블 사이에 텍스트가 존재하는가
            # pass
            # 조건 4 : 두 테이블의 세로축이 하나라도 일치하는가
            # y_value = tables[index-1][0][1]
            vs_list = [[], []]
            for vs in vertical_segments:
                # if vs[]
                y_value = tables[index-1][0][1]
                if y_value <= vs[1] <= y_value + tables[index-1][0][-1] :
                    vs_list[0].append( vs[0] )
                y_value = tables[index][0][1]
                if y_value <= vs[1] <= y_value + tables[index][0][-1] :
                    vs_list[1].append( vs[0] )
                    
            for v in vs_list[0]:
                if v in vs_list[1]:
                    # print("tables[index-1][0]",tables[index-1][0])
                    isTable = True
                    # table_set.extend( [ tables[index-1][0], tables[index][0] ] )
                    # print("same vertical")
                    break
            # print("table_set",table_set)
            # result.append( table_set )
            # table_set = []
            
            if not isTable: continue
            # 조건 5 : 테이블 사이 간격이 테이블의 간격보다 작거나 같은가
            hs_list = [[], []]
            for hs in horizontal_segments:
                # if vs[]
                h_y_value = hs[1]
                
                y_value = tables[index-1][0][1]
                if y_value <= h_y_value <= y_value + tables[index-1][0][-1] :
                    hs_list[0].append( h_y_value )
                y_value = tables[index][0][1]
                if y_value <= h_y_value <= y_value + tables[index][0][-1] :
                    hs_list[1].append( h_y_value )
            # print("hs_list", hs_list)
            
            # 테이블 간격이 row 평균보다 넓으면 테이블 연속 아님
            top_value = tables[index-1][0][1]+tables[index-1][0][-1]
            bottom_value = tables[index][0][1]
            row_value1 = sum([hs_list[0][x-1] - hs_list[0][x] for x in range(1, len(hs_list[0]))]) / (len(hs_list[0])-1)
            row_value2 = sum([hs_list[1][x-1] - hs_list[1][x] for x in range(1, len(hs_list[1]))]) / (len(hs_list[1])-1)
            row_value = max( row_value1, row_value2 )
            table_by_table = bottom_value - top_value
            '''
            print("bottom_value",bottom_value)
            print("top_value",top_value)
            print("table_by_table",table_by_table)
            print("row_value",row_value)
            '''
            if table_by_table > row_value:
                continue
            else:
                table_set.extend( [ tables[index-1][0], tables[index][0] ] )
            
            result.append( table_set )
            table_set = []
            
        #print("result", result)
    return result
    
    
def addVerticalLine(vertical_mask, merge_table, size=2):
    for table in merge_table:
        x_value1 = table[0][0]
        x_value2 = table[0][0] + table[0][2]
        y_value1 = table[0][1]
        y_value2 = table[-1][1]
        
        vertical_mask[y_value1:y_value2+size, x_value1-size:x_value1+size] = 255
        vertical_mask[y_value1:y_value2+size, x_value2-size:x_value2+size] = 255
        
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
    
    '''

