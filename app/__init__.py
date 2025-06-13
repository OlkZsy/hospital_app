from flask import Flask, redirect, url_for, render_template
from config import Config
from app.extensions import db, login_manager

# blueprint imports
from app.routes.auth import auth_bp
from app.routes.lekarz import lekarz_bp
from app.routes.pacjent import pacjent_bp
from app.routes.administrator import administrator_bp

# model imports
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.models.wizyta import Wizyta
from app.models.recepta import Recepta
from app.models.historia import HistoriaMedyczna
from app.models.harmonogram import HarmonogramLekarza
from app.models.recepcjonista import Recepcjonista
from app.routes.recepcjonista import recepcjonista_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'

    ######
    @login_manager.user_loader
    def load_user(user_id):
        try:
            if user_id.startswith('admin_'):
                id_num = int(user_id.replace('admin_', ''))
                return Administrator.query.get(id_num)
            elif user_id.startswith('lekarz_'):
                id_num = int(user_id.replace('lekarz_', ''))
                return Lekarz.query.get(id_num)
            elif user_id.startswith('pacjent_'):
                id_num = int(user_id.replace('pacjent_', ''))
                return Pacjent.query.get(id_num)
            elif user_id.startswith('recepcjonista_'):
                id_num = int(user_id.replace('recepcjonista_', ''))
                return Recepcjonista.query.get(id_num)
        except:
            pass
        return None

    #blueprint reg
    app.register_blueprint(auth_bp)
    app.register_blueprint(lekarz_bp)
    app.register_blueprint(pacjent_bp)
    app.register_blueprint(administrator_bp)
    app.register_blueprint(recepcjonista_bp)



    # Главная страница - переадресация на логин
    @app.route('/')
    def index():
        return redirect(url_for('auth_bp.login'))

    # Дополнительные переадресации
    @app.route('/index')
    @app.route('/home')
    def home():
        return redirect(url_for('auth_bp.login'))

    return app