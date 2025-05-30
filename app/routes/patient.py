from flask import Blueprint, render_template
from flask_login import login_required, current_user

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'patient':
        return "Access Denied", 403
    return render_template('dashboards/patient.html', user=current_user)
