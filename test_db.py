from app import create_app, db
from app.models.timetable import Timetable
from app.models.user import Student, User

app = create_app()
with app.app_context():
    print("ALL TIMETABLE SLOTS:")
    slots = Timetable.query.all()
    for s in slots:
        print(f"ID:{s.id} | Section: '{s.class_section}' | Active: {s.is_active}")
    
    print("\nALL STUDENTS:")
    students = Student.query.all()
    for s in students:
        print(f"Student: {s.user.name} | Section: '{s.class_section}'")
