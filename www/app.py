#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-08
#

from flask import Flask, Blueprint
from .views import views

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views)
    return app