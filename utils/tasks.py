# -*- coding: utf-8 -*-
#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-16
# Last modified on 2021-03-29
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

from camelot.parsers import Stream
from check_lattice.Lattice_2 import Lattice2

from camelot.ext.ghostscript import Ghostscript

from flask import session

from PyPDF2 import PdfFileReader, PdfFileWriter
from camelot.utils import get_page_layout, get_text_objects, get_rotation
from utils.location import get_file_dim, get_regions, get_regions_img, bbox_to_areas

# from .utils.file import mkdirs

def split(originalFilePath, PDFS_FOLDER, split_progress, line_scale=40, pages='all'):
    try:
        extract_pages, total_pages = get_pages(originalFilePath, pages)

        (
            filenames,
            imagenames,
            imagepaths,
            filedims,
            imagedims,
            detected_areas,
        ) = ({} for i in range(6))

        for page in extract_pages:
            progress = int( page / total_pages * 100 )
            split_progress['progress'] = progress

            # extract into single-page PDF
            save_page(originalFilePath, page)
            
            filename = f"page-{page}.pdf"
            filepath = os.path.join(PDFS_FOLDER, filename)

            imagename = "".join( [filename.replace(".pdf", ""), ".png"] )
            thumb_imagename = "".join( [filename.replace(".pdf", ""), "-thumb.png"] )
            imagepath = os.path.join(PDFS_FOLDER, imagename)
            thumb_imagepath = os.path.join(PDFS_FOLDER, thumb_imagename)

            # convert single-page PDF to PNG

            gs_call = "-q -sDEVICE=png16m -o {} -r300 {}".format(imagepath, filepath)
            gs_call = gs_call.encode().split()
            null = open(os.devnull, "wb")
            with Ghostscript(*gs_call, stdout=null) as gs:
                pass
            null.close()

            # creating thumbnail image
            gs_call = "-q -sDEVICE=png16m -o {} -r50 {}".format(thumb_imagepath, filepath)
            gs_call = gs_call.encode().split()
            null = open(os.devnull, "wb")
            with Ghostscript(*gs_call, stdout=null) as gs:
                pass
            null.close()
            #################

            filedims[page] = get_file_dim(filepath)
            imagedims[page] = get_image_dim(imagepath)
            
            # lattice
            parser = Lattice2(line_scale=line_scale)
            tables = parser.extract_tables(filepath)

            detected_areas[page] = tables
        return detected_areas
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