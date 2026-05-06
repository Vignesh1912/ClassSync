from datetime import datetime, timezone
from backend import db

class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time_limit = db.Column(db.DateTime, nullable=False)
    classroom_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius_meters = db.Column(db.Float, default=50.0)
    status = db.Column(db.String(20), default='active') # active/expired/closed
    total_present = db.Column(db.Integer, default=0)
    class_section = db.Column(db.String(100), nullable=True)  # e.g. 'Semester 4 - CSE Delta'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        def _iso_utc(dt):
            if not dt: return None
            iso = dt.isoformat()
            return iso + 'Z' if not dt.tzinfo else iso

        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'subject_id': self.subject_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'start_time': _iso_utc(self.start_time),
            'end_time_limit': _iso_utc(self.end_time_limit),
            'classroom_name': self.classroom_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius_meters': self.radius_meters,
            'status': self.status,
            'total_present': self.total_present,
            'class_section': self.class_section
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    student_latitude = db.Column(db.Float, nullable=False)
    student_longitude = db.Column(db.Float, nullable=False)
    distance_from_class = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='present') # present/rejected
    is_valid = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='uix_session_student'),
    )

class SessionActivityLog(db.Model):
    __tablename__ = 'session_activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False) # marked/rejected/attempt
    reason = db.Column(db.String(255), nullable=True) # E.g., 'Outside radius (105m vs 50m max)'
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
