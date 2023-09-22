
import os

# Classe utilizzata per caricare le configurazioni dell'src
class Config:
    SECRET_KEY = 'a41ea9cd7d293df959ff1af31fd07394'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../static/uploads')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True

    REDIS_URL = "redis://localhost:6379/0"


