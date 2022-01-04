#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2022-01-05
#

import cv2
import os
import json

from flask import (
    Flask,
    request,
    render_template,
    jsonify,
    Blueprint,
    redirect,
    url_for,
    current_app,
    session
)
import matplotlib.pyplot as plt
import numpy as np
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader


from utils.file_path import file_path_select
from utils.location import (
    get_file_dim,
    get_regions,
    get_regions_img,
    bbox_to_areas
)
from utils.tasks import split as task_split
from check_lattice.Lattice_2 import Lattice2
from check_lattice.check_line_scale import GetLineScale
from data_rendering.makeGoogleSheet import make_google_sheets


views = Blueprint("views", __name__)
split_progress = {} # split 작업 진행도
detected_areas = {}


# 기본 인덱스 페이지, 이곳에서 pdf파일을 업로드할 수 있음
@views.route("/", methods=['GET'])
def index():
    return render_template('index.html')

    # 예시 페이지로 리다이렉트시킴 (현재 사용 안함)
    # return redirect(url_for('views.example'))
    

# 각종 테스트 페이지. 현재 사용안함
@views.route("/test", methods=['GET'])
def test():
    return render_template('test.html')


# table_shape.pdf파일로 테스트하던 예시 페이지
@views.route("/example", methods=['GET'])
def example():
    page = request.args.get("page")
    if page is None:
        page = "166"
    
    return render_template('example.html', page=page)


# jquery ajax로 파일 업로드 요청시 오게되는 라우트
@views.route("/uploadPDF", methods = ['POST'])
def uploadPDF():
    global split_progress
    global detected_areas

    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.files.getlist('file')

    errors = {}
    success = False
    filepath = None

    for file in files:
        if file:
            # secure_filename은 한글명을 지원하지 않음
            # filename = secure_filename(file.filename)
            filename = file.filename
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                filename
            )
            file_page_path = os.path.splitext(filepath)[0]

            # make filename folder
            if not os.path.exists(file_page_path):
                os.makedirs(file_page_path)

            filepath = os.path.join(file_page_path, filename)
            
            # pdf file save (with uploaded)
            file.save(filepath)
            success = True

        else:
            errors[file.filename] = 'File type is not allowed'
    
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 206
        return resp

    # main 
    if success:
        # original pdf -> split 1, 2 .... n page pdf
        
        inputstream = open(filepath, "rb")
        infile = PdfFileReader(inputstream, strict=False)
        total_page = infile.getNumPages()
        inputstream.close()
        empty_pages = []

        result = task_split(filepath, file_page_path, split_progress)

        if result is not None and len(result) > 0:
            v = {}
            for page, tables in result.items():
                bboxs = []

                page_file = file_page_path + f"\\page-{page}.pdf"
                image_file = file_page_path + f"\\page-{page}.png"

                (
                    v['imageHeight'],
                    v['imageWidth'],
                    _
                ) = cv2.imread(image_file).shape

                for table in tables:
                    bbox = table._bbox
                    bboxs.append(
                        bbox_to_areas(v, bbox, page_file)
                        + f",{v['imageWidth']},{v['imageHeight']}"
                    )
                    
                bboxs = ";".join(bboxs)
                result[page] = bboxs

            # for page in [str(i) for i in range(1, total_page+1)]:
            # for page in range(1, total_page+1):
            
            for page in result.keys():
                if result.get(page) is None or result.get(page) == '':
                    empty_pages.append(page)

            print('@'*50)
            print(empty_pages)
            session['empty_pages'] = empty_pages
            print(f'total length: {total_page}\
                \tempty length:{len(empty_pages)}')
            print('@'*50)
            
        else:
            bboxs = 0

        detected_areas[filename.replace('.pdf', '')] = result

        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp

    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


# progress 진행도를 반환하는 라우트
@views.route('/getProgress', methods = ['POST'])
def getProgress():
    global split_progress

    result = split_progress.get('progress')
    return jsonify(result)


# 추출할 pdf파일이 정해졌을때 추출을 진행하는 라우트 (Get 요청으로 pdf파일 명시)
@views.route("/extract_page", methods=['GET'])
def extract_page():
    global detected_areas

    fileName = request.args.get("fileName")
    # page = request.args.get("page")
    # if page is None:
    #     page = 1

    # if fileName is not None and page is not None:
    if fileName is not None:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], fileName)
        file_page_path = os.path.splitext(filepath)[0]
        filepath = os.path.join(file_page_path, fileName+'.pdf')
        
        inputstream = open(filepath, "rb")
        infile = PdfFileReader(inputstream, strict=False)
        total_page = infile.getNumPages()
        inputstream.close()

        return render_template(
            'extract.html',
            fileName=fileName,
            totalPage=total_page,
            detected_areas=detected_areas[fileName],
            # page=page
        )

    else:
        return render_template(
            'error.html',
            error='해당 페이지를 찾을 수 없습니다.'
        )



@views.route("/pre_extract", methods=['POST'])
def pre_extract():
    global detected_areas

    file_name = request.form['fileName']+".pdf"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
    file_page_path = os.path.splitext(filepath)[0]
    filepath = os.path.join(file_page_path, file_name)
    empty_pages = session['empty_pages']
    total_page = len(empty_pages)
    empty_pages = ','.join([str(i) for i in empty_pages])

    line_scale = int(request.form['line_scale'])
    result = task_split(
        filepath,
        file_page_path,
        split_progress,
        line_scale = line_scale,
        pages = empty_pages
    )

    empty_pages = []

    if result is not None and len(result) > 0:
        v = {}
        for page, tables in result.items():
            bboxs = []

            page_file = file_page_path + f"\\page-{page}.pdf"
            image_file = file_page_path + f"\\page-{page}.png"

            (
                v['imageHeight'],
                v['imageWidth'],
                _
            ) = cv2.imread(image_file).shape

            for table in tables:
                bbox = table._bbox
                bboxs.append(
                    bbox_to_areas(v, bbox, page_file)
                    +f",{v['imageWidth']},{v['imageHeight']}"
                )
                
            bboxs = ";".join(bboxs)
            result[page] = bboxs
        
        for page in result.keys():
            if result.get(page) is None or result.get(page) == '':
                empty_pages.append(page)

        print('@'*50)
        print(empty_pages)
        session['empty_pages'] = empty_pages
        print(f'total length: {total_page}\tempty length:{len(empty_pages)}')
        print('@'*50)
        
    else:
        bboxs = 0

    detected_areas[file_name.replace('.pdf', '')] = result

    resp = jsonify({'message' : 'success'})
    resp.status_code = 201
    return resp







# 추출할 pdf파일이 정해졌을때 추출을 진행하는 라우트 (Get 요청으로 pdf파일 명시)
@views.route("/pre_extract_page", methods=['GET'])
def pre_extract_page():
    fileName = request.args.get("fileName")

    # if fileName is not None and page is not None:
    if fileName is not None:
        empty_pages = session['empty_pages']

        return render_template(
            'pre_extract.html',
            fileName=fileName,
            empty_pages=empty_pages
        )

    else:
        return render_template(
            'error.html',
            error='해당 페이지를 찾을 수 없습니다.'
        )


# 타겟 pdf 페이지 1장의 테이블을 추출하는 라우트
@views.route("/doExtract", methods=['POST'])
def doExtract_page():
    if request.method == 'POST':
        page = request.form['page']
        file_name = request.form['fileName']
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)

        page_file = f"{filepath}\\page-{page}.pdf"
    
        table_option = request.form['table_option']
        line_scale = request.form['line_scale']
        
        jsons = request.form['jsons']
        jsons = json.loads(jsons)
        
        regions = []
        for k, v in jsons.items():
            v = json.loads(v)
            regions.append( get_regions(v, page_file) )

        result = extract(regions, page_file, table_option, line_scale)
        
        if len(result) > 0:
            html = []
            jsons = []
            csvs = []
            col_width = []
            table_width = []
            bboxs = []
            gs = []

            for idx, table in enumerate(result, 1):
                df = table.df
                df.reset_index(drop=True, inplace=True)

                gs.append(table)

                html.append( df.to_html(index=False, header=False).replace('\\n', '<br>') )

                cols, width_sum = getWidth(df)
                col_width.append( cols )
                table_width.append( width_sum )
                csvs.append( df.to_csv(index=False) )
                df.to_csv(f'{filepath}\\page-{page}-table-{idx}.csv', index=False)

                
                bbox = table._bbox
                bboxs.append( bbox_to_areas(v, bbox, page_file) )
                
            html = "<br>".join(html)
            bboxs = ";".join(bboxs)

            # 구글시트 호출
            gs_url = make_google_sheets(file_name, gs, header='c')
            
        else:
            html = "<span>발견된 테이블 없음</span>"
            bboxs = 0
            
        return jsonify({'html':html, 'bboxs':bboxs, 'jsons':jsons, 'col_width':col_width, 'table_width':table_width, 'csvs':csvs, 'gs_url':gs_url})
        # return jsonify({'html':html, 'bboxs':bboxs, 'gs_url':gs_url})


# 라인스케일 요청시 적절한 값 반환해주는 라우트
@views.route("/getLineScale", methods=['POST'])
def get_line_scale():
    if request.method == 'POST':
        file_name = request.form['fileName']
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
        imgname = f"{filepath}\\page-{request.form['page']}.png"
        
        
        jsons = request.form['jsons']
        jsons = json.loads(jsons)
        
        regions = []
        for k, v in jsons.items():
            v = json.loads(v)
            regions.append( get_regions_img(v, imgname) )

        regions = [ int(float(i)) for i in regions[0].split(',') ]
        
        getlinescale = GetLineScale(imgname, regions)
        print("line size >", getlinescale.line_size)
        print("adapted line scale >", getlinescale.line_scale)
            
        return jsonify({'line_scale':getlinescale.line_scale})


# 지정 pdf파일 지정 영역의 테이블을 추출하는 함수
def extract(regions, page_file, table_option, line_scale=40):
    # output_camelot = read_pdf(page_file, flavor="lattice", table_regions=regions)
    tables = None
    line_scale = int(line_scale)
    
    if table_option == "areas":
        parser = Lattice2(table_areas=regions, line_scale=line_scale)
        
    else:
        parser = Lattice2(table_regions=regions, line_scale=line_scale)
    tables = parser.extract_tables(page_file)
    
    return tables





import math

'''
Main 함수
pandas dataFrame을 인자로 받아 Google Sheet에 연결하여 시트를 생성,
그리고 생성된 cell의 너비와 높이를 데이터에 맞게 변경해 주는 함수
input   : dataFrame(Pandas DataFrame)
output  : new Google Sheet
'''
def getWidth(dataFrame) :
    rows = len(dataFrame) + 1   # + 1 은 Column 열임
    cols = len(dataFrame.columns)

    maxWidth = 0
    maxHeight = 0

    result = []
    width_sum = 0

    for col in range(cols): 
        maxWidth = 0
        for row in range(rows):
            # Cell 객체에 접근하면 소요시간 오래걸려 dataFrame 값에 접근
            if(row == 0) : # row가 0인 경우 > column cell일때
                value = dataFrame.columns[col]
            else :
                value = dataFrame.iloc[row - 1, col]
            value = str(value)

            width = GetProperWidth(value, 14)
            if(width > maxWidth) :
                maxWidth = width

        # result.append({'type':'text', 'width':maxWidth})
        result.append({'width':str(maxWidth)+'px'})
        width_sum += maxWidth

    return result, width_sum

    # 행 높이를 설정해주는 구현문
    # 작동은 잘 되지만, google sheet가 자동으로 cell 높이을 잡아줌
    # 나중에 사용시 주석 해제하고 사용할 것
    # for row in range(rows):
        # maxHeight = 0
        # for col in range(cols):
           # if(row == 0):
               # value = dataFrame.columns[col]
           # else :
               # value = dataFrame.iloc[row - 1, col]

           # value = str(value)
           # height = GetProperHeight(value, fontSize)
           # if(height > maxHeight) :
               # maxHeight = height
       # gsFormat.set_row_height(workSheet, str(row + 1), maxHeight)

'''
GetFontSize 함수
format 객체를 받아서 String으로 형 변환 후, fontSize를 인덱싱해 값을 반환
input   : format(class: Format)
output  : fontSize(Integer)
'''
def GetFontSize(format) :
    format = str(format)
    attributes = format.split(';')
    fontSize = ""
    for char in attributes[10]: # 10번째 속성이 fontSize 속성임
        if char.isdecimal(): # str에서 숫자만 추출
            fontSize += char
    
    return int(fontSize)


'''
GetColAdr 함수
column 값을 숫자로 받아서 해당 숫자에 맞는 열 문자를 반환
input   : col(Interger)
output  : address(String)
'''
def GetColAdr(col) :
    address = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26) # 26 == 알파벳 개수
        address = chr(65 + remainder) + address
    return address


'''
GetProperWidth 함수
text와 fontSize를 인자로 받아 셀의 적정 너비를 계산하는 함수
input   : text(String), fontSize(Integer)
output  : maxWidth(Integer) 
'''
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


'''
GetProperHeight 함수
text와 fontSize를 인자로 받아 셀의 적정 높이를 계산하는 함수
input   : text(String), fontSize(Integer)
output  : height(Integer) 
'''
def GetProperHeight(text, fontSize) :
    lineList = text.splitlines()
    lineCount = len(lineList)
    PIXEL = 1.566 # 한줄당 글자의 높이 
    MARGIN = 5.34 # Cell의 여백

    height = ((PIXEL * fontSize) * lineCount) + MARGIN

    return int(height)