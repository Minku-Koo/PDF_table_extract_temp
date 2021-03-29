import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import Cell
import pandas as pd
from gspread_formatting import *
import os

def make_google_sheets(tables, header=None, email=None, **kwargs):
    '''
    sheet_name : sheet name
    header : Bold text A or 1 1
    '''    

    json_file = './data_rendering/astute-cumulus-158007-52b32148e4df.json'
    sheet_name = ""
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/13g5-I80S4LV3aV-w6Mo6LkjrGTJoSrxBxG6BSqyMS00/edit#gid='

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
    
    batch = batch_updater(doc)
    
    try:
        doc.add_worksheet(title="Temp", rows="1", cols="1")
    except:
        print("already exist Temp")
    
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
        sheet_name = str(i)
        try:
            result = doc.add_worksheet(title=sheet_name, rows="100", cols="100")
            ws = doc.worksheet(sheet_name)
            np_table = tables[i].to_numpy()
        except:
            doc.del_worksheet(doc.worksheet(str(i)))
            result = doc.add_worksheet(title=sheet_name, rows="100", cols="100")
            ws = doc.worksheet(sheet_name)
            count = count + 1
            np_table = tables[i].to_numpy()
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
        #format_cell_range(ws,[(ran[0],fmt_top), (ran[1],fmt_bottom), (ran[2],fmt_left), (ran[3],fmt_right)])
        batch.format_cell_range(ws, ran[0],fmt_top)
        batch.format_cell_range(ws, ran[1],fmt_bottom)
        batch.format_cell_range(ws, ran[2],fmt_left)
        batch.format_cell_range(ws, ran[3],fmt_right)
        batch.execute()
    doc.del_worksheet(doc.get_worksheet(0))

    ws_list = []
    i=0
    while 1:
        try:
            if doc.get_worksheet(i) == None:
                break
            ws_list.append(doc.get_worksheet(i).id)
            i=i+1
        except:
            break
    return [spreadsheet_url+str(l) for l in ws_list]

