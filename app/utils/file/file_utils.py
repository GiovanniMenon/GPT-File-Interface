
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from datetime import datetime

import os
from docx import Document
import json

from app.utils.message_utils import send_sse_message


def allowed_file(filename, extension):
    # Dato un filename e una estensione ritorna True se il file e' di quel tipo

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in extension


def path_file(file):
    # Dato un file ritorna la path a quel file

    from flask import current_app as app
    from flask import session
    return os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), secure_filename(file.filename))


def create_path(ext, type):
    # Data l'estensione di un file crea una path unica a quel file.abs
    # Type serve a dividere tra file di translate e file audio. 

    from flask import current_app as app
    from flask import session
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    unique_filename = os.urandom(5).hex() + "_" + timestamp + ext
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), type, unique_filename)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    return file_path


def folder_path(type):
    # Dato un tipo ritorna la sua folder

    from flask import current_app as app
    from flask import session
    return os.path.join(app.config['UPLOAD_FOLDER'], str(session["ID_USER"]), type)


def save_file(file, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    file.save(file_path)


def write_file(text, type):
    doc = Document()
    doc.add_paragraph(text)
    file_path = create_path(".docx", type)
    relative_path = os.path.relpath(file_path, start="myprog")
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    doc.save(file_path)
    return relative_path


def remove_selected_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def is_audio(file_name):
    # Controlla che un file sia Audio

    return allowed_file(file_name, {"mp3", "mpga", 'mpeg', "m4a", 'wav', 'webm'})


def log_context_to_file(file_path, context):
    # Salava e aggiorna il Log con il contesto appena cancellato

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


def clear_file_folder(folder_path):
    # Data la path di una cartella la cancella

    if not os.path.exists(folder_path):
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Errore durante l'eliminazione di {filename}: {e}")


def split_audio(path, chunk_length=16 * 60 * 1000):
    # Dato un audio lo divide in parti di 15min e ritorna un lista di path a queste parti

    send_sse_message("bar", "Divido il file in sotto parti", 45, 'audio')
    audio = AudioSegment.from_file(path)
    length_audio = len(audio)
    chunks = [audio[i:i + chunk_length] for i in range(0, length_audio, chunk_length)]

    compressed_files = []
    for chunk in chunks:
        output_file_name = create_path(".mp3", "audio_folder")
        chunk.export(output_file_name, format="mp3")
        compressed_files.append(output_file_name)

    send_sse_message("bar", "Trascrivo il file", 50, 'audio')
    return compressed_files


def compress_audio(input_path, format="mp3"):
    # Dato un file audio lo comprime e ritorna il nuovo path al file

    send_sse_message("bar", "Comprimo il file", 35, 'audio')
    audio = AudioSegment.from_file(input_path)
    output_file = create_path(".mp3", "audio_folder")
    audio.export(output_file, format=format, bitrate="64k")
    return output_file
