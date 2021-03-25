#
# get_file_path_select.py
# PDF_table_extract
#
# Created by Ji-yong219 on 2021-03-08
# Last modified on 2021-03-09
#

import copy
from camelot.parsers import Lattice, Stream
from camelot.utils import (
    scale_image,
    scale_pdf
)
from camelot.image_processing import (
    adaptive_threshold,
    find_lines,
    find_contours,
    find_joints,
)

from check_lattice.make_border import addOutline # call module
from check_lattice.merge_table import tableMerge, addVerticalLine # call module

class Lattice2(Lattice):
    
    def _generate_table_bbox(self):
        def scale_areas(areas):
            scaled_areas = []
            for area in areas:
                x1, y1, x2, y2 = area.split(",")
                x1 = float(x1)
                y1 = float(y1)
                x2 = float(x2)
                y2 = float(y2)
                x1, y1, x2, y2 = scale_pdf((x1, y1, x2, y2), image_scalers)
                scaled_areas.append((x1, y1, abs(x2 - x1), abs(y2 - y1)))
            return scaled_areas

        self.image, self.threshold = adaptive_threshold(
            self.imagename,
            process_background=self.process_background,
            blocksize=self.threshold_blocksize,
            c=self.threshold_constant,
        )

        image_width = self.image.shape[1]
        image_height = self.image.shape[0]
        image_width_scaler = image_width / float(self.pdf_width)
        image_height_scaler = image_height / float(self.pdf_height)
        pdf_width_scaler = self.pdf_width / float(image_width)
        pdf_height_scaler = self.pdf_height / float(image_height)
        image_scalers = (image_width_scaler, image_height_scaler, self.pdf_height)
        pdf_scalers = (pdf_width_scaler, pdf_height_scaler, image_height)

        if self.table_areas is None:
            regions = None
            if self.table_regions is not None:
                regions = scale_areas(self.table_regions)

            vertical_mask, vertical_segments = find_lines(
                self.threshold,
                regions=regions,
                direction="vertical",
                line_scale=self.line_scale,
                iterations=self.iterations,
            )
            horizontal_mask, horizontal_segments = find_lines(
                self.threshold,
                regions=regions,
                direction="horizontal",
                line_scale=self.line_scale,
                iterations=self.iterations,
            )

            contours = find_contours(vertical_mask, horizontal_mask)

            # vertical and horizontal mask are made from find_lines()
            
            vertical_mask = addOutline("v", vertical_mask, contours)
            horizontal_mask = addOutline("h", horizontal_mask, contours)
            print("table merge start2")
            # after addOutline
            contours = find_contours(vertical_mask, horizontal_mask)
            
            # addVerticalList = tableMerge(contours, vertical_segments, horizontal_segments)
            # vertical_mask = addVerticalLine(vertical_mask, addVerticalList)

            # contours = find_contours(vertical_mask, horizontal_mask)

            table_bbox = find_joints(contours, vertical_mask, horizontal_mask)
        else:
            vertical_mask, vertical_segments = find_lines(
                self.threshold,
                direction="vertical",
                line_scale=self.line_scale,
                iterations=self.iterations,
            )
            horizontal_mask, horizontal_segments = find_lines(
                self.threshold,
                direction="horizontal",
                line_scale=self.line_scale,
                iterations=self.iterations,
            )

            areas = scale_areas(self.table_areas)
            
            vertical_mask = addOutline("v", vertical_mask, areas) # maybe
            horizontal_mask = addOutline("h", horizontal_mask, areas) # maybe
            print("table merge start")
            # after addOutline
            contours = find_contours(vertical_mask, horizontal_mask)
            
            # addVerticalList = tableMerge(contours, vertical_segments, horizontal_segments)
            # vertical_mask = addVerticalLine(vertical_mask, addVerticalList)

            areas = find_contours(vertical_mask, horizontal_mask)

            table_bbox = find_joints(areas, vertical_mask, horizontal_mask)

        self.table_bbox_unscaled = copy.deepcopy(table_bbox)

        self.table_bbox, self.vertical_segments, self.horizontal_segments = scale_image(
            table_bbox, vertical_segments, horizontal_segments, pdf_scalers
        )