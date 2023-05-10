# Copyright (c) 2023, DoloresJuliana and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from pathlib import Path
import imghdr


class TFFDocument(Document):
	pass

@frappe.whitelist()
def get_document(document_name):
	return frappe.get_doc("TFF Document", document_name)

@frappe.whitelist()
def get_doctype(document_classification):
	return frappe.db.get_value("TFF Classification", document_classification, "document_type")

@frappe.whitelist()
def text_capture(document_name):
	tffd_details: TFFDocument = frappe.get_doc("TFF Document", document_name)
	file = frappe.get_site_path() + tffd_details.document_file
	tffd_details.document_text = get_textinfile(file)
	tffd_details.save()

	return {"text_length": len(tffd_details.document_text)}

def get_textinfile(file):
	if imghdr.what(file) or Path(file).suffix == ".pdf": 
		return get_text_image_or_pdf(file)
	else: 
		return None

def get_text_image_or_pdf(file):
	from pibitff.utils.file_extraction import TffOCRExtractor
	extractor = TffOCRExtractor()
	data = extractor.extract_html(file, lang="spa+eng")
	return data

"""
def get_textinpdf(file):
	from langchain.document_loaders.pdf import UnstructuredPDFLoader
	loader = UnstructuredPDFLoader(file)
	data = ' '.join(map(str, loader.load()))
	return data
"""