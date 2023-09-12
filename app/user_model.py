
from app import db
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    elements_chat = db.Column(JSON)
    elements_translate = db.Column(JSON)
    elements_audio = db.Column(JSON)
    file_context = db.Column(JSON)
    context = db.Column(JSON)

    def __init__(self, username, password):
        self.username = username
        self.password = password
