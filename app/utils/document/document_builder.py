
from app.utils.file.file_utils import write_file


def document_translate_builder(text):
    from flask import session
    from app.utils.manager_utils import translate_manager

    text = translate_manager(text, session['LANGUAGE_OPTION_CHOOSE'])
    path_trascription = write_file(text, "translate_folder")

    words = text.split()
    if len(words) > 100:
        result_print = " ".join(words[:100])
        result_print += " ...."
    else:
        result_print = text
    session['ELEMENTS_TRANSLATE'].append({'response_text': result_print,
                                          'link_text': "<a href='" + path_trascription + "' id='cont_ai_chat_file' \
                                      style='display:block;' download> <pre> Scarica il File : " +
                                                       " <i class='fa-solid fa-file'></i></pre> </a>"})
