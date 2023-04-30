# Copyright (c) 2023, DoloresJuliana and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from pathlib import Path
import imghdr
import os

class TFFDocument(Document):
	pass

@frappe.whitelist()
def get_document(document_name):
	return frappe.get_doc("TFF Document", document_name)

@frappe.whitelist()
def text_capture(document_name):
	tffd_details: TFFDocument = frappe.get_doc("TFF Document", document_name)
	file = frappe.get_site_path() + tffd_details.document_file
	tffd_details.document_text = get_textinfile(file)
	tffd_details.save()

	return {"text_length": len(tffd_details.document_text)}

def get_textinfile(file):
	if imghdr.what(file): return get_textinimage(file)
	elif Path(file).suffix == ".pdf": return get_textinpdf(file)
	else: return None

def get_textinpdf(file):
	from langchain.document_loaders import UnstructuredPDFLoader
	loader = UnstructuredPDFLoader(file)
	data = loader.load()
	return data

def get_textinimage(file):
	from langchain.document_loaders.image import UnstructuredImageLoader
	loader = UnstructuredImageLoader(file)
	data = loader.load()
	return data[0]