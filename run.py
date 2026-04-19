from backend import create_app, db
from backend.models.user import User, Student, Teacher, Subject
from backend.models.timetable import Timetable
from backend.models.attendance import AttendanceSession, Attendance, SessionActivityLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Student': Student, 'Teacher': Teacher, 'Subject': Subject, 'Timetable': Timetable}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
