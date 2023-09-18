
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.app_config import Config
from flask_sse import sse

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    Session(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.user_model import User
        return User.query.get(int(user_id))

    from app.main.routes import main
    from app.auth.auth_routes import auth

    app.register_blueprint(main)

    app.register_blueprint(sse, url_prefix='/stream')
    app.register_blueprint(auth, url_prefix='/auth')

    return app
