# -*- coding: utf-8 -*-
#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-16
# Last modified on 2021-03-16
#

import os
import glob
import json
import logging
import subprocess
import datetime as dt
import cv2

import camelot
from camelot.core import TableList
from camelot.parsers import Lattice, Stream
from camelot.ext.ghostscript import Ghostscript

from flask import session

from PyPDF2 import PdfFileReader, PdfFileWriter
from camelot.utils import get_page_layout, get_text_objects, get_rotation

# from .utils.file import mkdirs

class TaskProgress():
    progress = 0

    def __init__(self):
        pass

    def setProgress(self, progress):
        self.progress = progress

    def getProgress(self):
        return self.progress

    def split(self, originalFilePath, PDFS_FOLDER):
        try:
            extract_pages, total_pages = get_pages(originalFilePath, 'all')

            (
                filenames,
                imagenames,
                imagepaths,
                filedims,
                imagedims,
                detected_areas,
            ) = ({} for i in range(6))

            for page in extract_pages:
                # self.setProgress( total_pages / page * 100 )
                session['progress'] = total_pages / page * 100

                # extract into single-page PDF
                save_page(originalFilePath, page)
                
                filename = f"page-{page}.pdf"
                filepath = os.path.join(PDFS_FOLDER, filename)

                imagename = "".join([filename.replace(".pdf", ""), ".png"])
                imagepath = os.path.join(PDFS_FOLDER, imagename)

                # convert single-page PDF to PNG
                gs_call = "-q -sDEVICE=png16m -o {} -r300 {}".format(imagepath, filepath)
                gs_call = gs_call.encode().split()
                null = open(os.devnull, "wb")
                with Ghostscript(*gs_call, stdout=null) as gs:
                    pass
                null.close()

                # filenames[page] = filename
                # filepaths[page] = filepath
                # imagenames[page] = imagename
                # imagepaths[page] = imagepath

                # filedims[page] = get_file_dim(filepath)
                # imagedims[page] = get_image_dim(imagepath)

                # lattice_areas, stream_areas = (None for i in range(2))
                # lattice
                # parser = Lattice()
                # tables = parser.extract_tables(filepath)
                # if len(tables):
                #     lattice_areas = []
                #     for table in tables:
                #         x1, y1, x2, y2 = table._bbox
                #         lattice_areas.append((x1, y2, x2, y1))

                # detected_areas[page] = {"lattice": lattice_areas, "stream": stream_areas}

            # file.extract_pages = json.dumps(extract_pages)
            # file.total_pages = total_pages
            # file.has_image = True
            # file.filenames = json.dumps(filenames)
            # file.filepaths = json.dumps(filepaths)
            # file.imagenames = json.dumps(imagenames)
            # file.imagepaths = json.dumps(imagepaths)
            # file.filedims = json.dumps(filedims)
            # file.imagedims = json.dumps(imagedims)
            # file.detected_areas = json.dumps(detected_areas)
        except Exception as e:
            logging.exception(e)



def get_pages(filename, pages):
    """Converts pages string to list of ints.

    Parameters
    ----------
    filename : str
        Path to PDF file.
    pages : str, optional (default: '1')
        Comma-separated page numbers.
        Example: 1,3,4 or 1,4-end.

    Returns
    -------
    N : int
        Total pages.
    P : list
        List of int page numbers.

    """
    page_numbers = []
    inputstream = open(filename, "rb")
    infile = PdfFileReader(inputstream, strict=False)
    N = infile.getNumPages()
    if pages == "1":
        page_numbers.append({"start": 1, "end": 1})
    else:
        # if infile.isEncrypted:
        #     infile.decrypt(password)
        if pages == "all":
            page_numbers.append({"start": 1, "end": infile.getNumPages()})
        else:
            for r in pages.split(","):
                if "-" in r:
                    a, b = r.split("-")
                    if b == "end":
                        b = infile.getNumPages()
                    page_numbers.append({"start": int(a), "end": int(b)})
                else:
                    page_numbers.append({"start": int(r), "end": int(r)})
    inputstream.close()
    P = []
    for p in page_numbers:
        P.extend(range(p["start"], p["end"] + 1))
    return sorted(set(P)), N


def save_page(filepath, page_number):
    infile = PdfFileReader(open(filepath, "rb"), strict=False)
    page = infile.getPage(page_number - 1)
    outfile = PdfFileWriter()
    outfile.addPage(page)
    outpath = os.path.join(os.path.dirname(filepath), "page-{}.pdf".format(page_number))
    with open(outpath, "wb") as f:
        outfile.write(f)
    froot, fext = os.path.splitext(outpath)
    layout, __ = get_page_layout(outpath)
    # fix rotated PDF
    chars = get_text_objects(layout, ltype="char")
    horizontal_text = get_text_objects(layout, ltype="horizontal_text")
    vertical_text = get_text_objects(layout, ltype="vertical_text")
    rotation = get_rotation(chars, horizontal_text, vertical_text)
    if rotation != "":
        outpath_new = "".join([froot.replace("page", "p"), "_rotated", fext])
        os.rename(outpath, outpath_new)
        infile = PdfFileReader(open(outpath_new, "rb"), strict=False)
        if infile.isEncrypted:
            infile.decrypt("")
        outfile = PdfFileWriter()
        p = infile.getPage(0)
        if rotation == "anticlockwise":
            p.rotateClockwise(90)
        elif rotation == "clockwise":
            p.rotateCounterClockwise(90)
        outfile.addPage(p)
        with open(outpath, "wb") as f:
            outfile.write(f)


def get_file_dim(filepath):
    layout, dimensions = get_page_layout(filepath)
    return list(dimensions)


def get_image_dim(imagepath):
    image = cv2.imread(imagepath)
    return [image.shape[1], image.shape[0]]



def extract(job_id):
    try:
        job = session.query(Job).filter(Job.job_id == job_id).first()
        rule = session.query(Rule).filter(Rule.rule_id == job.rule_id).first()
        file = session.query(File).filter(File.file_id == job.file_id).first()

        rule_options = json.loads(rule.rule_options)
        flavor = rule_options.pop("flavor")
        pages = rule_options.pop("pages")

        tables = []
        filepaths = json.loads(file.filepaths)
        for p in pages:
            kwargs = pages[p]
            kwargs.update(rule_options)
            parser = (
                Lattice(**kwargs) if flavor.lower() == "lattice" else Stream(**kwargs)
            )
            t = parser.extract_tables(filepaths[p])
            for _t in t:
                _t.page = int(p)
            tables.extend(t)
        tables = TableList(tables)

        froot, fext = os.path.splitext(file.filename)
        datapath = os.path.dirname(file.filepath)
        for f in ["csv", "excel", "json", "html"]:
            f_datapath = os.path.join(datapath, f)
            mkdirs(f_datapath)
            ext = f if f != "excel" else "xlsx"
            f_datapath = os.path.join(f_datapath, "{}.{}".format(froot, ext))
            tables.export(f_datapath, f=f, compress=True)

        # for render
        jsonpath = os.path.join(datapath, "json")
        jsonpath = os.path.join(jsonpath, "{}.json".format(froot))
        tables.export(jsonpath, f="json")
        render_files = {
            os.path.splitext(os.path.basename(f))[0]: f
            for f in glob.glob(os.path.join(datapath, "json/*.json"))
        }

        job.datapath = datapath
        job.render_files = json.dumps(render_files)
        job.is_finished = True
        job.finished_at = dt.datetime.now()

        session.commit()
        session.close()
    except Exception as e:
        logging.exception(e)
