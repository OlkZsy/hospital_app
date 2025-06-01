from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.routes.auth import auth_bp
from app.routes.patient import patient_bp
from app.routes.doctor import doctor_bp
from app.routes.admin import admin_bp
from app.models import User




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.models.pacjent import Pacjent
    from app.models.lekarz import Lekarz
    from app.models.recepcjonista import Recepcjonista
    from app.models.administrator import Administrator
    from app.models.wizyta import Wizyta
    from app.models.recepta import Recepta
    from app.models.historia import HistoriaMedyczna
    from app.models.harmonogram import HarmonogramLekarza




    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    from app.routes.treatment import treatment_bp
    app.register_blueprint(treatment_bp)

    return app
