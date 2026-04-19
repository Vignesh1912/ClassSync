from app import create_app, db
from app.models.user import User, Subject

app = create_app()
with app.app_context():
    u = User.query.filter(User.name.like('%Swaruuu%')).first()
    if u:
        print(f"User: {u.name}")
        print(f"Department: '{u.department}'")  # Use quotes to see spaces
        
        subjs = Subject.query.filter_by(department=u.department).all()
        print(f"Subjects matching '{u.department}': {len(subjs)}")
        for s in subjs:
            print(f"  - ID: {s.id} | Code: '{s.subject_code}' | Name: '{s.subject_name}' | Dept: '{s.department}'")
    else:
        print("User Swaruuu Sir not found!")
