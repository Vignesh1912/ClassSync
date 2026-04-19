from datetime import datetime, timezone
from backend import db

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    classroom_link = db.Column(db.String(500), nullable=True)
    resource_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_subject=False, include_submission_count=False):
        d = {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'subject_id': self.subject_id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat(),
            'classroom_link': self.classroom_link,
            'resource_path': self.resource_path,
            'created_at': self.created_at.isoformat(),
        }
        if include_subject:
            from backend.models.user import Subject
            subject = Subject.query.get(self.subject_id)
            d['subject_name'] = subject.subject_name if subject else 'Unknown'
            d['subject_code'] = subject.subject_code if subject else ''
        if include_submission_count:
            total = len(self.submissions)
            submitted = sum(1 for s in self.submissions if s.status == 'submitted')
            d['total_students'] = total
            d['submitted_count'] = submitted
        return d


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    self_reported = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending / submitted

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uix_assignment_student'),
    )


class NotificationPrefs(db.Model):
    __tablename__ = 'notification_prefs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    email_enabled = db.Column(db.Boolean, default=True)
    remind_3days = db.Column(db.Boolean, default=True)
    remind_2days = db.Column(db.Boolean, default=True)
    remind_1day = db.Column(db.Boolean, default=True)
    remind_deadline = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('notification_prefs', uselist=False))
