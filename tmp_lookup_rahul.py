from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.filter(User.name.ilike('%Rahul%')).all()
    if not users:
        print("No user found with name containing 'Rahul'")
    for u in users:
        print(f"FOUND: ID={u.id} | Name={u.name} | Email={u.email} | Role={u.role}")
