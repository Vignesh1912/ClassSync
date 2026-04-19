from app import create_app, db
from app.models.user import User, Student, Teacher, Subject

app = create_app()

with app.app_context():
    # Clean previous just in case
    db.drop_all()
    db.create_all()

    # Subjects
    s1 = Subject(subject_code='CS101', subject_name='Introduction to Computer Science', credits=3, semester=1, department='CSE')
    s2 = Subject(subject_code='CS102', subject_name='Data Structures', credits=4, semester=2, department='CSE')
    db.session.add_all([s1, s2])
    
    # STUDENT
    student = User(name='Rahul Mehta', email='rahul@college.edu', role='student', department='CSE', college_user_id='STU-1234')
    student.set_password('password')
    db.session.add(student)
    db.session.flush()
    student_profile = Student(user_id=student.id, class_section='Semester 4 - CSE Alpha', semester=4, roll_number='21CSE100', batch='2021-2025')
    db.session.add(student_profile)

    # TEACHER
    teacher = User(name='Dr. Sharma', email='sharma@college.edu', role='teacher', department='CSE', college_user_id='TCH-1234')
    teacher.set_password('password')
    db.session.add(teacher)
    db.session.flush()
    teacher_profile = Teacher(user_id=teacher.id, designation='Assistant Professor', cabin_no='A-201')
    db.session.add(teacher_profile)

    # HOD
    hod = User(name='Prof. Iyer', email='iyer@college.edu', role='hod', department='CSE', college_user_id='HOD-1234')
    hod.set_password('password')
    db.session.add(hod)

    # ADMIN
    admin = User(name='System Admin', email='admin@classsync.app', role='admin', department='Admin', college_user_id='ADM-1234')
    admin.set_password('password')
    db.session.add(admin)

    db.session.commit()
    print("Database seeded with demo users!")
