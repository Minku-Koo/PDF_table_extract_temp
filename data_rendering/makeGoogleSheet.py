import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Cell
import camelot
import pandas as pd
from gspread_formatting import *
import math

def make_google_sheets(sheet_name, tables, header=None, email=None, **kwargs):
    '''
    sheet_name : sheet name
    header : Bold text A or 1 1
    '''    
    json_file = './data_rendering/astute-cumulus-158007-52b32148e4df.json'
    #json_file = 'astute-cumulus-158007-52b32148e4df.json'

    doc = create_sheets(json_file, sheet_name)
    batch = batch_updater(doc)

    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{doc.id}/edit#gid="

    input_data(tables, sheet_name, doc, batch, header)
    doc.del_worksheet(doc.get_worksheet(0))
    i = 0
    ws_list = []

    while 1:
        try:
            if doc.get_worksheet(i) == None:
                break
            ws_list.append(doc.get_worksheet(i).id)
            i=i+1
        except:
            break

    return [spreadsheet_url+str(l) for l in ws_list]
    
def GetProperWidth(text, fontSize) : # Cell의 적정 길이를 반환하는 함수
    # 글자크기가 1pt일때 가로길이 구분
    # pt1p322 이면 글자크기가 1pt일때 가로길이 1.322pt임
    # margin은 셀의 여백임.

    lineList = text.splitlines()

    PT1P322 = ('@') # margin 7.78pt
  # PT1P312 = 한글 + margin 7.206pt
    PT1P155 = ('%') # margin 7.45pt
    PT1P122 = ('W') # margin 7.8
    PT1P088 = ('m', 'M') # margin 7.12pt
    PT1P022 = ('G', 'O', 'Q') # margin 6.78pt
    PT0P933 = ('w', 'C', 'D', 'H', 'N', 'R', 'U')  # margin 7.67pt
    PT0P866 = ('&', 'A', 'B', 'D', 'E', 'K', 'P', 'S', 'V', 'X', 'Y') # margin 7.34pt
    PT0P800 = ('F', 'T', 'Z') # margin 7pt
    PT0P755 = ('L') # margin 6.45pt
    PT0P733 = ('a', 'b', 'c', 'd', 'e', 'g', 'h', 'k', 'n', 'o', 'p', 
               'q', 's', 'u', 'v', 'x', 'y', 'z', '?', '=', '_', '#', 
               '$', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0') # margin 6.67pt
    PT0P644 = ('J') # margin 7.56pt
    PT0P611 = ('+', '^') # margin 6.89pt
    PT0P511 = ('*') # margin 6.89pt
    PT0P455 = ('\"') # margin 7.45pt
    PT0P355 = ('f', 'r', 't', ' ', '!', '\'', '[', ']', '/', ';', ':', 
               '-', '\\', '(', ')', ',', '.', '`', 'I', '·', '‘','’') # margin 7.45pt
    PT0P288 = ('i', 'j', 'l') # margin 7.12pt

    maxWidth = 0

    for line in lineList:
        
        width = 0
        textPixel = 0
        margin = 0
        length = len(line)
        
        if(length <= 0) :
            continue

        for c in line: # 문장의 한 글자씩 검수함
            if c in PT1P322 :
                textPixel += fontSize * 1.322
                margin += 7.78
            elif c in PT1P155 :
                textPixel += fontSize * 1.155
                margin += 7.45
            elif c in PT1P122 :
                textPixel += fontSize * 1.122
                margin += 7.8
            elif c in PT1P088 :
                textPixel += fontSize * 1.088
                margin += 7.12
            elif c in PT1P022 :
                textPixel += fontSize * 1.022
                margin += 6.78
            elif c in PT0P933 :
                textPixel += fontSize * 0.933
                margin += 7.67
            elif c in PT0P866 :
                textPixel += fontSize * 0.866
                margin += 7.34
            elif c in PT0P800 :
                textPixel += fontSize * 0.8
                margin += 7
            elif c in PT0P755 :
                textPixel += fontSize * 0.755
                margin += 6.45
            elif c in PT0P733 :
                textPixel += fontSize * 0.733
                margin += 6.67
            elif c in PT0P644 :
                textPixel += fontSize * 0.644
                margin += 7.56
            elif c in PT0P611 :
                textPixel += fontSize * 0.611
                margin += 6.89
            elif c in PT0P511 :
                textPixel += fontSize * 0.511
                margin += 6.89
            elif c in PT0P455 :
                textPixel += fontSize * 0.455
                margin += 7.45
            elif c in PT0P355 :
                textPixel += fontSize * 0.355
                margin += 7.45
            elif c in PT0P288 :
                textPixel += fontSize * 0.288
                margin += 7.12
            else : # 나머지 한글, 유니코드 기호들 > 대부분 한글 넓이와 같음
                textPixel += fontSize * 1.312
                margin += 7.206 
        margin = margin / len(line) # 각 폰트별 margin값 참고, 평균 margin값 산출
        width = math.ceil((textPixel + margin) * 1.01)
        if(width > maxWidth) :
            maxWidth = width
            
    return maxWidth

def GetColAdr(col) :
    address = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26) # 26 == 알파벳 개수
        address = chr(65 + remainder) + address
    return address

# def get_font_size(format) :
#     format = str(format)
#     attributes = format.split(';')
#     fontSize = ""
#     for char in attributes[10]: # 10번째 속성이 fontSize 속성임
#         if char.isdecimal(): # str에서 숫자만 추출
#             fontSize += char
    
#     return int(fontSize)

def input_data(tables, sheet_name, doc, batch, header):
    fmt = cellFormat(
        backgroundColor=color(1, 0.9, 0.9),
        #horizontalAlignment='CENTER'
        )
    fmt_top = cellFormat(borders=Borders(top=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_bottom = cellFormat(borders=Borders(bottom=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_left = cellFormat(borders=Borders(left=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_right = cellFormat(borders=Borders(right=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')    

    for i in range(len(tables)):
        page = tables[i].parsing_report['page']
        order = tables[i].parsing_report['order']
        
        result = doc.add_worksheet(title=sheet_name+f"_{page}_{order}", rows="100", cols="100")
        ws = doc.worksheet(sheet_name+f"_{page}_{order}")
        np_table = tables[i].df.to_numpy()
        
        # default_format = get_default_format(ws)
        font_size = 10
        
        if header != None:
            if header == "r":
                range_header = 'A1:'+chr(ord('A')+np_table.shape[1]-1)+"1"                
                batch.format_cell_range(ws, range_header, fmt)
                set_frozen(ws, rows=1)
                ws.format('1', {'textFormat': {'bold': True}})
            elif header == "c":
                range_header = 'A1:'+'A'+str(np_table.shape[0])     
                batch.format_cell_range(ws, range_header, fmt)
                set_frozen(ws, cols=1)
                ws.format('A', {'textFormat': {'bold': True}})
            elif header == "rc" or header == "cr":
                range_header = 'A1:'+chr(ord('A')+np_table.shape[1]-1)+"1"
                batch.format_cell_range(ws, range_header, fmt)
                ws.format('1', {'textFormat': {'bold': True}})
                ws.format('A', {'textFormat': {'bold': True}})
                range_header = 'A1:'+'A'+str(np_table.shape[0])
                batch.format_cell_range(ws, range_header, fmt)
                set_frozen(ws, cols=1, rows=1)
            else:
                print("Wrong header option")

        
        total_width = 0
        cells = []
        for x in range(len(np_table)):
            for y in range(len(np_table[1])):
                cells.append(Cell(row=x+1, col=y+1, value=np_table[x][y]))
        ws.update_cells(cells)
        ran = ['A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0])]
        # format_cell_range(ws,[(ran[0],fmt_top), (ran[1],fmt_bottom), (ran[2],fmt_left), (ran[3],fmt_right)])
        batch.format_cell_range(ws, ran[0],fmt_top)
        batch.format_cell_range(ws, ran[1],fmt_bottom)
        batch.format_cell_range(ws, ran[2],fmt_left)
        batch.format_cell_range(ws, ran[3],fmt_right)

        for y in range(len(np_table[1])):
            maxWidth = 0
            for x in range(len(np_table)):
                value = np_table[x][y]
                value = str(value)
                width = GetProperWidth(value, font_size)
                
                if(width > maxWidth) :
                    maxWidth = width
                
            total_width += maxWidth

            batch.set_column_width(ws, GetColAdr(y+1), maxWidth)

    batch.execute()

        

def create_sheets(json_file, sheet_name):
    gc = gspread.service_account(json_file)
    doc = gc.create(sheet_name)
    doc.share(value=None,perm_type='anyone', role='writer')

    return doc 

# tables = camelot.read_pdf("table.pdf", pages="166-168")
# print(make_google_sheets("table.pdf", tables, header="r"))