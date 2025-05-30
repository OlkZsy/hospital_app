from flask import Blueprint, render_template
from flask_login import login_required, current_user

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'doctor':
        return "Access Denied", 403
    return render_template('dashboards/doctor.html', user=current_user)
