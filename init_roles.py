from app import create_app
from app.extensions import db
from app.models import Role

app = create_app()

with app.app_context():
    roles = ['admin', 'doctor', 'patient']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
            print(f"Role '{role_name}' added.")
    db.session.commit()
    print("Initializaton complete.")