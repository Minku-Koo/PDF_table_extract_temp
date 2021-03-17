#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-17
#

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
from werkzeug.utils import secure_filename

from utils.file_path import file_path_select
from utils.location import get_file_dim, get_regions, get_regions_img, bbox_to_areas
from utils.tasks import split as pdf_split

from check_lattice.Lattice_2 import Lattice2
from check_lattice.check_line_scale import GetLineScale

from PyPDF2 import PdfFileReader

import cv2
import os
import json
import matplotlib.pyplot as plt
import numpy as np


views = Blueprint("views", __name__)
split_progress = {} # split 작업 진행도


# 기본 인덱스 페이지, 이곳에서 pdf파일을 업로드할 수 있음
@views.route("/", methods=['GET'])
def index():
    return render_template('index.html')
    # return redirect(url_for('views.example')) # 예시 페이지로 리다이렉트시킴 (현재 사용 안함)
    

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
            # filename = secure_filename(file.filename) # secure_filename은 한글명을 지원하지 않음
            filename = file.filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
        # extract() # 이부분에 작업 넣으면 좋을 듯
        # original pdf -> split 1, 2 .... n page pdf
        pdf_split(filepath, file_page_path, split_progress)

        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp

    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


@views.route('/getProgress', methods = ['POST'])
def getProgress():
    global split_progress

    result = split_progress.get('progress')
    return jsonify(result)

# 추출할 pdf파일이 정해졌을때 추출을 진행하는 라우트 (Get 요청으로 pdf파일 명시)
@views.route("/extract_page", methods=['GET'])
def extract_page():
    fileName = request.args.get("fileName")
    page = request.args.get("page")

    if page is None:
        page = 1

    if fileName is not None and page is not None:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], fileName)
        file_page_path = os.path.splitext(filepath)[0]
        filepath = os.path.join(file_page_path, fileName+'.pdf')
        
        inputstream = open(filepath, "rb")
        infile = PdfFileReader(inputstream, strict=False)
        total_page = infile.getNumPages()
        inputstream.close()

        return render_template('extract.html', fileName=fileName, page=page, totalPage=total_page)

    else:
        return render_template('error.html', error='해당 페이지를 찾을 수 없습니다.')


# 타겟 pdf 페이지 1장의 테이블을 추출하는 라우트
@views.route("/doExtract", methods=['POST'])
def doExtract_page():
    if request.method == 'POST':
        file_name = request.form['fileName']
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)

        page_file = f"{filepath}\\page-{request.form['page']}.pdf"
    
        table_option = request.form['table_option']
        line_scale = request.form['line_scale']
        
        jsons = request.form['jsons']
        jsons = json.loads(jsons)
        
        regions = []
        for k, v in jsons.items():
            v = json.loads(v)
        
        result = extract(regions, page_file, table_option, line_scale)
        
        if len(result) > 0:
            html = []
            bboxs = []
            for table in result:
                df = table.df
                df.reset_index(drop=True, inplace=True)
                html.append( df.to_html(index=False, header=False).replace('\\n', '<br>') )
                
                bbox = table._bbox
                bboxs.append( bbox_to_areas(v, bbox, page_file) )
                
            html = "<br>".join(html)
            bboxs = ";".join(bboxs)
            
        else:
            html = "<span>발견된 테이블 없음</span>"
            bboxs = 0
            
        return jsonify({'html':html, 'bboxs':bboxs})

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


def extract(regions, page_file, table_option, line_scale=30):
    # output_camelot = read_pdf(page_file, flavor="lattice", table_regions=regions)
    tables = None
    line_scale = int(line_scale)
    
    if table_option == "areas":
        parser = Lattice2(table_areas=regions, line_scale=line_scale)
        
    else:
        parser = Lattice2(table_regions=regions, line_scale=line_scale)
    tables = parser.extract_tables(page_file)
    
    return tables