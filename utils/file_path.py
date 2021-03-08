#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-08
#

from tkinter import Tk
from tkinter.filedialog import askopenfilename

def file_path_select():
    root = Tk() # GUI로 파일경로를 선택하기위해 tkinter 라는 라이브러리 사용
    # GUI로 파일 선택 창이 나옴
    root.fileName = askopenfilename( filetypes=(("pdf file", "*.pdf"), ("all", "*.*")) ) #pdf 파일만 불러옴
    pdf_path = root.fileName
    root.destroy()  #gui 창 닫기
    return pdf_path #원하는 파일 경로 반환