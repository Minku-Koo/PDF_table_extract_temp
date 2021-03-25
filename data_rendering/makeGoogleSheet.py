import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Cell
import camelot
import pandas as pd
from gspread_formatting import *

def make_google_sheet(json_file,tables, speradsheet_url,  header=None, email=None, **kwargs):
    '''
    sheet_name : sheet name
    header : Bold text A or 1 1
    '''    
    print(kwargs)
    fmt = cellFormat(
        backgroundColor=color(1, 0.9, 0.9),
        horizontalAlignment='CENTER'
        )
    fmt_top = cellFormat(borders=Borders(top=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_bottom = cellFormat(borders=Borders(bottom=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_left = cellFormat(borders=Borders(left=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')
    fmt_right = cellFormat(borders=Borders(right=Border("SOLID", Color(0, 0, 0, 0))))#, horizontalAlignment='CENTER')    
    
    gc = gspread.service_account(json_file)
    doc = gc.open_by_url(spreadsheet_url)
    i = 0
    ws_list = []
    
    doc.add_worksheet(title="Temp",rows="1", cols="1")

    batch = batch_updater(doc)
    print(spreadsheet_url)
    while 1:
        try:
            if doc.get_worksheet(i) == None:
                break
            ws_list.append(doc.get_worksheet(i).id)
            i=i+1
        except:
            break
    count = 0
    for i in range(len(tables)):
        try:
            result = doc.add_worksheet(title=str(i)+"번", rows="100", cols="100")
            ws = doc.worksheet(str(i)+"번")
            np_table = tables[i].to_numpy()
        except:
            doc.del_worksheet(doc.worksheet(str(i)+"번"))
            result = doc.add_worksheet(title=str(i)+"번", rows="100", cols="100")
            ws = doc.worksheet(str(i)+"번")
            count = count + 1
            np_table = tables[i].to_numpy()
            # if header != None:
            #     if header == "r":
            #         range_header = 'A1:'+chr(ord('A')+np_table.shape[1]-1)+"1"                
            #         batch.format_cell_range(ws, range_header, fmt)
            #         set_frozen(ws, rows=1)
            #         ws.format('1', {'textFormat': {'bold': True}})
            #     elif header == "c":
            #         range_header = 'A1:'+'A'+str(np_table.shape[0])     
            #         batch.format_cell_range(ws, range_header, fmt)
            #         set_frozen(ws, cols=1)
            #         ws.format('A', {'textFormat': {'bold': True}})
            #     elif header == "rc" or header == "cr":
            #         range_header = 'A1:'+chr(ord('A')+np_table.shape[1]-1)+"1"
            #         batch.format_cell_range(ws, range_header, fmt)
            #         ws.format('1', {'textFormat': {'bold': True}})
            #         ws.format('A', {'textFormat': {'bold': True}})
            #         range_header = 'A1:'+'A'+str(np_table.shape[0])
            #         batch.format_cell_range(ws, range_header, fmt)
            #         set_frozen(ws, cols=1, rows=1)
            #     else:
            #         print("Wrong header option")
            
        cells = []
        for i in range(len(np_table)):
            for j in range(len(np_table[1])):
                cells.append(Cell(row=i+1, col=j+1, value=np_table[i][j]))
        ws.update_cells(cells)
        # ran = ['A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0])]
        # format_cell_range(ws,[(ran[0],fmt_top), (ran[1],fmt_bottom), (ran[2],fmt_left), (ran[3],fmt_right)])
        # batch.format_cell_range(ws, ran[0],fmt_top)
        # batch.format_cell_range(ws, ran[1],fmt_bottom)
        # batch.format_cell_range(ws, ran[2],fmt_left)
        # batch.format_cell_range(ws, ran[3],fmt_right)
        # batch.execute()
    #doc.del_worksheet(doc.get_worksheet(0))
    print(len(ws_list), count)
    for i in range(len(ws_list)-count):
        doc.del_worksheet(doc.get_worksheet(0))

    ws_list = []
    while 1:
        try:
            if doc.get_worksheet(i) == None:
                break
            ws_list.append(doc.get_worksheet(i).id)
            i=i+1
        except:
            break
    return ws_list

# a = pd.DataFrame([['1','2','3'],['4','5','6'],['7','8','9']])
# b = pd.DataFrame([['a','b','c'],['d','e','f'],['h','i','j']])
# c = pd.DataFrame([['박지용','구민구','이현무'],['1','2','3'],['a','b','c']])
# d = pd.DataFrame([['박지용2','구민구','이현무'],['1','2','3'],['a','b','c']])
json_file_name = 'astute-cumulus-158007-52b32148e4df.json'
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/13g5-I80S4LV3aV-w6Mo6LkjrGTJoSrxBxG6BSqyMS00/edit#gid=0'

result = google_sheets(json_file_name,  tables, spreadsheet_url, header="c")

