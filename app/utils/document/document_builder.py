from app.utils.document.document_utils import docx_file_translate_gpt, docx_file_translate_google
from app.utils.parser.parser import extract_text_from_docx, write_text_to_docx
from app.utils.message_utils import send_sse_message


def document_translate_builder(path_):
    # Data una path elabora il file docx e ritorna il file docx Tradotto

    from flask import session

    send_sse_message("Divido il file in parti", 40, "trans")
    parts = extract_text_from_docx(path_)
    if session['MODEL_TRANS_MODEL'] == 'Google-AI':
        translations = docx_file_translate_google(parts, session['LANGUAGE_OPTION_CHOOSE'] ) # Remove
    else:
        translations = docx_file_translate_gpt(parts, session['LANGUAGE_OPTION_CHOOSE'])

    send_sse_message("Ricostruisco il file" , 100 , "trans") 
    path_to_file = write_text_to_docx(path_, translations, 'translate_folder')
    session['ELEMENTS_TRANSLATE'].append({'response_text': "Documento:",
                                          'link_text': "<a href='" + path_to_file + "' id='cont_ai_chat_file' \
                                          style='display:block;' download> <pre> Scarica il Documento Tradotto" +
                                          " <i class='fs-1 fa-solid fa-file-word'></i></pre> </a>"})
