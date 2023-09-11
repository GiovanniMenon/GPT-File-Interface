
from app.utils.file.file_utils import allowed_file
import docx
from docx import Document
import pandas as pd
from PyPDF2 import PdfReader


def extract_file_content(file_path, file_name):
    if allowed_file(file_name, {"xls", 'xlsx'}):
        df = pd.read_excel(file_path)
        file_text = df.to_string()
    elif allowed_file(file_name, {"csv"}):
        df = pd.read_csv(file_path)
        file_text = df.to_string()
    elif allowed_file(file_name, {"docx"}):
        doc = docx.Document(file_path)
        file_text = ""
        for paragraph in doc.paragraphs:
            file_text += paragraph.text + "\n"
    elif allowed_file(file_name, {"pdf"}):
        file_text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_text = f.read()
            if isinstance(file_text, bytes):
                file_text = file_text.decode('utf-8')
    return file_text


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
            
    return text