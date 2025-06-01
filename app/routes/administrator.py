from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'admin':
        return "Access Denied", 403
    return render_template('dashboards/admin.html', user=current_user)
from flask import Blueprint, render_template
from flask_login import login_required
from app.models.wizyta import Wizyta

administrator_bp = Blueprint('administrator', __name__, url_prefix='/administrator')

@administrator_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboards/administrator.html')

@administrator_bp.route('/wizyty')
@login_required
def wizyty():
    wizyty = Wizyta.query.order_by(Wizyta.data_wizyty).all()
    return render_template('administrator/wizyty.html', wizyty=wizyty)
