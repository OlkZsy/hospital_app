from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'admin':
        return "Access Denied", 403
    return render_template('dashboards/admin.html', user=current_user)
