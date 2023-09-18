
from app import db
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON

# Classe User salvata nel db 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Campi per controllare che un utente non abbia una richiesta gia' in corso.
    has_chat_request_in_progress = db.Column(db.Boolean, default=False)
    has_audio_request_in_progress = db.Column(db.Boolean, default=False)

    # Campi in cui vengono gli elementi delle chat da mostrare per ogni sezione.
    user_elements_chat = db.Column(JSON)
    user_elements_translate = db.Column(JSON)
    user_elements_audio = db.Column(JSON)

    # Campi che contengono il contesto. 
    user_file_in_context = db.Column(JSON)
    user_context = db.Column(JSON)

    def __init__(self, username, password):
        self.username = username
        self.password = password
