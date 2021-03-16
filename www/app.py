#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-08
#

from flask import Flask, Blueprint
from .views import views
import os

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views)
    app.secret_key = 'cju_dblab_sharp_16'

    UPLOAD_FOLDER = os.getcwd() + r'\www\static\job_pdf'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    return app