from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.lekarz import Lekarz
from app.models.wizyta import Wizyta
from app import db

lekarz_bp = Blueprint('lekarz', __name__, url_prefix='/lekarz')

@lekarz_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboards/lekarz.html', user=current_user)

@lekarz_bp.route('/wizyty')
@login_required
def wizyty():
    wizyty = Wizyta.query.filter_by(id_lekarza=current_user.id_lekarza).order_by(Wizyta.data_wizyty).all()
    return render_template('lekarz/wizyty.html', wizyty=wizyty)
