from app import create_app, db
from app.models.user import User, Subject, Teacher
from app.models.timetable import Timetable

app = create_app()
with app.app_context():
    # Find teachers named Swaruuu
    teachers = User.query.filter(User.name.like('%Swaruuu%')).all()
    print(f"Total Matches: {len(teachers)}")
    for t in teachers:
        print(f"Teacher: {t.name} (ID: {t.id}) | Dept: {t.department}")
        if t.teacher_profile:
             print(f"  Teacher Profile ID: {t.teacher_profile.id}")
             slots = Timetable.query.filter_by(teacher_id=t.teacher_profile.id).all()
             print(f"  Timetable slots: {len(slots)}")
             for slot in slots:
                 subj = Subject.query.get(slot.subject_id)
                 print(f"    - slot: {subj.subject_name if subj else 'Unknown'} ({slot.class_section})")
        if t.department:
            subjs = Subject.query.filter_by(department=t.department).all()
            print(f"  Subjects in Dept '{t.department}': {len(subjs)}")
        else:
            print("  No department set for User!")

    all_subjects = Subject.query.all()
    print(f"\nTotal Subjects in DB: {len(all_subjects)}")
    for s in all_subjects:
        print(f"  - {s.subject_name} | Dept: {s.department} | Code: {s.subject_code}")
