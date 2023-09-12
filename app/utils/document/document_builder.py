from app.utils.document.document_utils import docx_file_translate
from app.utils.file.file_utils import write_file
from app.utils.parser.parser import extract_text_from_docx, write_text_to_docx


def document_translate_builder(path_):
    from flask import session
    from app.utils.manager_utils import translate_manager

    parts = extract_text_from_docx(path_)
    translations = docx_file_translate(parts, session['LANGUAGE_OPTION_CHOOSE'])
    path_to_file = write_text_to_docx(path_, translations)

    session['ELEMENTS_TRANSLATE'].append({'response_text': "Documento:",
                                          'link_text': "<a href='" + path_to_file + "' id='cont_ai_chat_file' \
                                      style='display:block;' download> <pre>" +
                                                       " <i class='fs-3 fa-solid fa-file'></i></pre> </a>"})
