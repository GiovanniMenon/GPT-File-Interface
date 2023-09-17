from app.utils.document.document_utils import docx_file_translate_gpt, docx_file_translate_google
from app.utils.parser.parser import extract_text_from_docx, write_text_to_docx


def document_translate_builder(path_):
    from flask import session

    parts = extract_text_from_docx(path_)
    if session['MODEL_TRANS_MODEL'] == 'Google-AI':
        print("Google-AI")
        translations = docx_file_translate_google(parts, session['LANGUAGE_OPTION_CHOOSE'] ) # Remove
    else:
        translations = docx_file_translate_gpt(parts, session['LANGUAGE_OPTION_CHOOSE'])


    path_to_file = write_text_to_docx(path_, translations, 'translate_folder')
    session['ELEMENTS_TRANSLATE'].append({'response_text': "Documento:",
                                          'link_text': "<a href='" + path_to_file + "' id='cont_ai_chat_file' \
                                          style='display:block;' download> <pre> Scarica il Documento Tradotto" +
                                          " <i class='fs-1 fa-solid fa-file-word'></i></pre> </a>"})
