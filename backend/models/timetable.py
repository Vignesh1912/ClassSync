from datetime import datetime, timezone
from backend import db

class Timetable(db.Model):
    __tablename__ = 'timetable'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    day_of_week = db.Column(db.String(20), nullable=False) # Monday/Tuesday/...
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    room_number = db.Column(db.String(50), nullable=False)
    class_section = db.Column(db.String(20), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    teacher = db.relationship('Teacher', backref=db.backref('timetable_slots', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('timetable_slots', lazy=True))

    def __repr__(self):
        return f'<Timetable {self.day_of_week} {self.start_time}-{self.end_time} {self.subject.subject_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.user.name if self.teacher else '',
            'subject_id': self.subject_id,
            'subject_name': self.subject.subject_name if self.subject else '',
            'subject_code': self.subject.subject_code if self.subject else '',
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else '',
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else '',
            'room_number': self.room_number,
            'class_section': self.class_section,
            'is_active': self.is_active
        }
