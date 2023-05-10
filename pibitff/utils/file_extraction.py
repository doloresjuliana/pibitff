# Copyright (c) 2023, DoloresJuliana and contributors
# For license information, please see license.txt

import pytesseract
import json
#import cv2
from cv2 import imread, resize, cvtColor, dilate, erode, INTER_CUBIC, COLOR_BGR2GRAY
import numpy as np
import os
from typing import BinaryIO, cast
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.utils import open_filename
from pdf2image import convert_from_path

class TffOCRExtractor:
    def __init__(self, tesseract_path=None):
        self.tesseract_path = tesseract_path
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def extract_text(self, image_path, lang="eng"):
        text = boxes = ""
        image_height = image_width = 0

        is_text_extractable = False
        if os.path.basename(image_path).split('.')[1] == "pdf":
            is_text_extractable = self.is_pdf_text_extractable(image_path)

        if is_text_extractable:
            text = str(self.get_pdf_pdfminer(image_path))
            if text == "":
                is_text_extractable = False
                image0_path = self.create_files_jpg(image_path)
                im = self.get_optimized_image(image0_path)
        else:
            im = self.get_optimized_image(image_path)

        if not is_text_extractable:
            image_height, image_width = im.shape
            new_file_pdf = self.create_file_pdf(image_path, lang, im)
            text = pytesseract.image_to_string(im, lang) 
            boxes = pytesseract.image_to_data(im, lang)

        output = {}
        output['page{}'.format(0)] = {
            'text': text, 
            'boxes': boxes,
            'image_width': image_width,
            'image_height': image_height
        }
        json_output = json.dumps(output, indent=4)
        return json_output
    
    def extract_lines(self, image_path, lang="eng"):
        json_input = json.loads(self.extract_text(image_path, lang))
        text = json_input["page0"]["text"]
        lines = text.split('\n')
        
        outls = {}
        x = 0
        for i, line in enumerate(lines):
            li = line.strip()
            if len(li):
                x += 1
                outls[x] = {"{}".format(li)}

        json_input["page0"]["text"] = outls
        json_output = json.dumps(json_input, default=tuple)
        return json_output

    def extract_html(self, image_path, lang="eng"):
        json_input = json.loads(self.extract_lines(image_path, lang))
        lines = {} 
        lines = json_input["page0"]["text"]
        num_lines = len(lines)
        image_height = int(json_input["page0"]["image_height"])
        #image_width = int(json_input["page0"]["image_width"])

        html_output = '<table>'
        if num_lines:
            line_height = int(image_height / 4 / num_lines)
            for j in range(num_lines):
                i = j + 1
                line = lines["{}".format(i)][0]
                html_output += '<tr style="height:{}px;">'.format(line_height)
                html_output += '<td>{}</td>'.format(line)
                html_output += '</tr>'
        html_output += '</table>'

        return html_output

    def get_optimized_image(self, image_path):
        # Read image using opencv
        img = imread(image_path)

        # Rescale the image, if needed.
        if img.shape[1] < 1191:
            f = int((1191 / img.shape[1]) * img.shape[0])
            dim = (1191, f)
            img = resize(img, dim, interpolation=INTER_CUBIC)

        # Convert to gray
        img = cvtColor(img, COLOR_BGR2GRAY)
        # Apply dilation and erosion to remove some noise
        kernel = np.ones((1, 1), np.uint8)
        img = dilate(img, kernel, iterations=1)
        img = erode(img, kernel, iterations=1)

        # Apply threshold to get image with only black and white
        # img = cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        return img
    
    def create_file_pdf(self, image_path, lang, im):
        # Extract the file name without the file extension
        file_name = os.path.basename(image_path).split('.')[0]
        file_name = file_name.split()[0]

        # Create a directory for outputs
        output_path = os.path.dirname(image_path) + "/tff"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Create a file searchable PDF
        new_file_pdf = output_path + "/" + file_name + ".pdf"
        pdf = pytesseract.image_to_pdf_or_hocr(im, lang=lang, extension='pdf')
        with open(new_file_pdf, 'w+b') as f:
            f.write(pdf)
        
        return new_file_pdf
    
    def create_files_jpg(self, image_path):
        # Extract the file name without the file extension
        file_name = os.path.basename(image_path).split('.')[0]
        file_name = file_name.split()[0]

        # Create a directory for outputs
        output_path = os.path.dirname(image_path) + "/tff/images"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Create a files jpg
        images = convert_from_path(image_path)
        for i in range(len(images)):
            images[i].save(output_path + "/" + file_name + '_page'+ str(i) +'.jpg', 'JPEG')

        new_file_jpg = output_path + "/" + file_name + '_page0.jpg'
        
        return new_file_jpg

    def get_pdf_pdfminer(self, image_path):
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.pdfdevice import PDFDevice
        from pdfminer.layout import LAParams, LTTextBox, LTTextLine
        from pdfminer.converter import PDFPageAggregator
        
        password = text = ""

        # Open and read, create object to parse, store content
        fp = open(image_path, "rb")
        parser = PDFParser(fp)
        document = PDFDocument(parser, password)

        # if not extractable, abort
        if not document.is_extractable:
            return ""
            
        # Create object that stores shared resources such as fonts or images
        rsrcmgr = PDFResourceManager()

        # set parameters for analysis
        laparams = LAParams()

        # Create a PDFDevice object which translates interpreted information into desired format
        # Device needs to be connected to resource manager to store shared resources
        # device = PDFDevice(rsrcmgr)
        # Extract the decive to page aggregator to get LT object elements
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create interpreter object to process page content from PDFDocument
        # Interpreter needs to be connected to resource manager for shared resources and device 
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Ok now that we have everything to process a pdf document, lets process it page by page
        for page in PDFPage.create_pages(document):
            # As the interpreter processes the page stored in PDFDocument object
            interpreter.process_page(page)
            # The device renders the layout from interpreter
            layout = device.get_result()
            # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    text += lt_obj.get_text()
                    
    
        fp.close()

        if text.encode("utf-8") == "b''":
            return ""
        return text

    def is_pdf_text_extractable(self, image_path: str = ""):

        def _fp_is_extractable(fp):
            try:
                next(PDFPage.get_pages(fp, check_extractable=True))
                extractable = True
            except PDFTextExtractionNotAllowed:
                extractable = False
            return extractable

        with open_filename(image_path, "rb") as fp:
            fp = cast(BinaryIO, fp)
            return _fp_is_extractable(fp)
