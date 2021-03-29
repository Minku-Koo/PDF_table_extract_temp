import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Cell
import camelot
import pandas as pd
from gspread_formatting import *

def make_google_sheets(sheet_name, json_file,tables, header=None, email=None, **kwargs):
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
    doc = gc.create(sheet_name)
    batch = batch_updater(doc)

    doc.share(value=None,perm_type='anyone', role='writer')
    spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{doc.id}"
    print(spreadsheet_url)

    for i in range(len(tables)):
        page = tables[i].parsing_report['page']
        order = tables[i].parsing_report['order']
        
        result = doc.add_worksheet(title=sheet_name+f"_{page}_{order}", rows="100", cols="100")
        ws = doc.worksheet(sheet_name+f"_{page}_{order}")
        np_table = tables[i].df.to_numpy()
        
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
        
        cells = []
        for i in range(len(np_table)):
            for j in range(len(np_table[1])):
                cells.append(Cell(row=i+1, col=j+1, value=np_table[i][j]))
        ws.update_cells(cells)
        ran = ['A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0]),'A1:'+chr(ord('A')+np_table.shape[1]-1)+str(np_table.shape[0])]
        # format_cell_range(ws,[(ran[0],fmt_top), (ran[1],fmt_bottom), (ran[2],fmt_left), (ran[3],fmt_right)])
        batch.format_cell_range(ws, ran[0],fmt_top)
        batch.format_cell_range(ws, ran[1],fmt_bottom)
        batch.format_cell_range(ws, ran[2],fmt_left)
        batch.format_cell_range(ws, ran[3],fmt_right)
        batch.execute()
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

    print(ws_list)

sheet_name = "table.pdf"
tables = camelot.read_pdf(sheet_name, flavor='lattice', pages='166-168')
json_file_name = 'astute-cumulus-158007-52b32148e4df.json'

make_google_sheets(sheet_name, json_file_name, tables, header="r")