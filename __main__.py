#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-08
#

from www.app import create_app

app = create_app()

app.debug = True
# app.run(host='lion.cju.ac.kr')
app.run(use_reloader=False)