from datetime import datetime, timezone
from backend import db, login
from flask_login import UserMixin
import bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum('student', 'teacher', 'hod', 'admin', name='user_roles'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    department = db.Column(db.String(100), nullable=True) # can be null for admin
    college_user_id = db.Column(db.String(50), index=True, unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.college_user_id} - {self.name}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_section = db.Column(db.String(20))
    semester = db.Column(db.Integer)
    roll_number = db.Column(db.String(50))
    batch = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

    def __repr__(self):
        return f'<Student {self.user.name}>'

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    designation = db.Column(db.String(100))
    cabin_no = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))

    def __repr__(self):
        return f'<Teacher {self.user.name}>'

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Subject {self.subject_code} - {self.subject_name}>'
