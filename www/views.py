#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-09
#

from flask import Flask, request, render_template, jsonify, Blueprint, redirect, url_for
import json
from utils.file_path import file_path_select
from utils.location import get_file_dim, get_regions, bbox_to_areas
from check_lattice.Lattice_2 import Lattice2

views = Blueprint("views", __name__)


@views.route("/", methods=['GET'])
def index():
    return redirect(url_for('views.example'))

@views.route("/example", methods=['GET'])
def example():
    page = request.args.get("page")
    if page is None:
        page = "166"
    
    return render_template('example.html', page=page)

@views.route("/extract", methods=['POST'])
def extract_page():
    if request.method == 'POST':
        # pdf_path = file_path_select() #PDF 파일 지정
        # file_name = pdf_path.split('/')[-1].split('.')[0]
        # page = "166"
        # page_file = os.path.join(
                # os.path.dirname(pdf_path),
                # os.path.basename(pdf_path).split(".")[0],
                # "page-"+str(page)+".pdf"
                # ).replace("\\", "/")
        # print(page_file)
        
        page_file = f"test_pdf/sample/table_shape/page-{request.form['page']}.pdf"
    
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