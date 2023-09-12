from app.utils.document.document_utils import docx_file_translate_gpt, docx_file_translate_google
from app.utils.file.file_utils import write_file
from app.utils.parser.parser import extract_text_from_docx, write_text_to_docx


def document_translate_builder(path_):
    from flask import session
    from app.utils.manager_utils import translate_manager

    path_to_file = ""

    if session['MODEL_TRANS_MODEL'] == 'Google-AI':
        print("1")
        path_to_file = docx_file_translate_google(path_, session['LANGUAGE_OPTION_CHOOSE'],'translate_folder')
    else:
        print("2")
        parts = extract_text_from_docx(path_)
        translations = docx_file_translate_gpt(parts, session['LANGUAGE_OPTION_CHOOSE'])
        path_to_file = write_text_to_docx(path_, translations, 'translate_folder')

    session['ELEMENTS_TRANSLATE'].append({'response_text': "Documento:",
                                          'link_text': "<a href='" + path_to_file + "' id='cont_ai_chat_file' \
                                          style='display:block;' download> <pre> Scarica il Documento Tradotto" +
                                          " <i class='fs-1 fa-solid fa-file-word'></i></pre> </a>"})
