from flask import Flask
from config import Config
from app.extensions import db, login_manager

# Blueprint imports
from app.routes.auth import auth_bp
from app.routes.lekarz import lekarz_bp
from app.routes.pacjent import pacjent_bp
from app.routes.administrator import administrator_bp

# Модельные импорты (чтобы Flask SQLAlchemy знал о таблицах)
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.models.wizyta import Wizyta
from app.models.recepta import Recepta
from app.models.historia import HistoriaMedyczna
from app.models.harmonogram import HarmonogramLekarza

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Настройка загрузчика пользователя
    @login_manager.user_loader
    def load_user(user_id):
        # Попытка загрузить пользователя из всех возможных 
        for model in [Pacjent, Lekarz, Recepcjonista, Administrator]:
            user = model.query.get(int(user_id))
            if user:
                return user
        return None

    #Blueprint reg
    app.register_blueprint(auth_bp)
    app.register_blueprint(lekarz_bp)
    app.register_blueprint(pacjent_bp)
    app.register_blueprint(administrator_bp)

    return app
