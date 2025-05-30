from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Treatment, User
from datetime import datetime

treatment_bp = Blueprint('treatment', __name__)

@treatment_bp.route('/treatment/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def manage_treatment(patient_id):
    patient = User.query.get_or_404(patient_id)
    if current_user.role.name == 'doctor':
        if request.method == 'POST':
            notes = request.form['notes']
            medications = request.form['medications']
            plan = request.form['plan']
            treatment = Treatment(
                patient_id=patient.id,
                doctor_id=current_user.id,
                date_assigned=datetime.utcnow(),
                notes=notes,
                medications=medications,
                plan=plan
            )
            db.session.add(treatment)
            db.session.commit()
            flash('Лечение назначено успешно.')
            return redirect(url_for('treatment.manage_treatment', patient_id=patient.id))
        treatments = Treatment.query.filter_by(patient_id=patient.id).all()
        return render_template('doctor/manage_treatment.html', patient=patient, treatments=treatments)
    elif current_user.role.name == 'patient' and current_user.id == patient.id:
        treatments = Treatment.query.filter_by(patient_id=patient.id).all()
        return render_template('patient/view_treatment.html', treatments=treatments)
    else:
        flash('У вас нет доступа к этой информации.')
        return redirect(url_for('main.index'))
