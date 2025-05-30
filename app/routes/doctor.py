from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Visit, db
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name != 'doctor':
        return "Access Denied", 403
    return render_template('dashboards/doctor.html', user=current_user)

@doctor_bp.route('/create-visit', methods=['GET', 'POST'])
@login_required
def create_visit():
    if current_user.role.name != 'doctor':
        return "Access Denied", 403

    patients = User.query.filter_by(role_id=3).all()  # patient role_id = 3

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        date = request.form['date']
        description = request.form['description']

        visit = Visit(
            doctor_id=current_user.id,
            patient_id=patient_id,
            date=datetime.fromisoformat(date),
            description=description
        )
        db.session.add(visit)
        db.session.commit()
        flash("Visit created successfully.")
        return redirect(url_for('doctor.dashboard'))

    return render_template('dashboards/create_visit.html', patients=patients)
