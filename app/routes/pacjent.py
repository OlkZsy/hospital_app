from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.wizyta import Wizyta
from app.models.pacjent import Pacjent

pacjent_bp = Blueprint('pacjent', __name__, url_prefix='/pacjent')

@pacjent_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboards/pacjent.html', user=current_user)

@pacjent_bp.route('/wizyty')
@login_required
def wizyty():
    wizyty = Wizyta.query.filter_by(id_pacjenta=current_user.id_pacjenta).order_by(Wizyta.data_wizyty).all()
    return render_template('pacjent/wizyty.html', wizyty=wizyty)
