from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models import Visit

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/visits')
@login_required
def get_visits():
    role = current_user.role.name
    visits = []

    if role == 'admin':
        visits = Visit.query.all()
    elif role == 'doctor':
        visits = Visit.query.filter_by(doctor_id=current_user.id).all()
    elif role == 'patient':
        visits = Visit.query.filter_by(patient_id=current_user.id).all()

    events = []
    for v in visits:
        events.append({
            'title': f'Visit with ID {v.id}',
            'start': v.date.isoformat(),
        })

    return jsonify(events)
