
from PyPDF2 import PdfReader
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from datetime import datetime
from moviepy.editor import VideoFileClip

import os
import pandas as pd
import docx
from docx import Document
import json


def allowed_file(filename, extension):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in extension


def path(file):
    from flask import current_app as app
    from flask import session
    return os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), secure_filename(file.filename))


def create_path():
    from flask import current_app as app
    from flask import session
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    unique_filename = os.urandom(5).hex() + "_" + timestamp + ".mp3"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), unique_filename)
    return file_path


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


def is_audio(file_name):

    return allowed_file(file_name, {"mp3", "mpga", 'mpeg', "m4a", 'wav', 'webm'})


def log_context_to_file(file_path, context):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    current_date = datetime.now().strftime('%Y-%m-%d')
    try:
        with open(file_path, 'r', encoding="UTF-8") as infile:
            data = json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if current_date not in data:
        data[current_date] = []

    data[current_date].append(context)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def save_file(file, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    file.save(file_path)


def remove_selected_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def write_file(text):
    from flask import current_app as app
    from flask import session

    doc = Document()
    doc.add_paragraph(text)
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    unique_filename = os.urandom(5).hex() + "_" + timestamp + ".docx"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), unique_filename)
    relative_path = os.path.relpath(file_path, start="myprog")
    doc.save(file_path)
    return relative_path


def performance(filename, lang, time):
    elapsed_time_formatted = "{:.4f}".format(time)
    data = f"{filename} | {lang} | {elapsed_time_formatted} s|\n"
    with open("performance.txt", "a") as file:
        file.write(data)


def compress_audio(path):
    input_audio = AudioSegment.from_file(path)

    # Comprimi l'audio utilizzando il codec MP3 con il bitrate desiderato
    file_path = create_path()
    compressed_audio = input_audio.export(file_path, format="mp3", bitrate="32k")
    remove_selected_file(path)

    return file_path

