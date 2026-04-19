from app import create_app, db
from app.models.timetable import Timetable

app = create_app()
with app.app_context():
    slots = Timetable.query.all()
    for s in slots:
        if s.class_section == "Semester 4- CSE Alpha":
            s.class_section = "Semester 4 - CSE Alpha"
            
    db.session.commit()
    print("Fixed timetable string mismatch.")
