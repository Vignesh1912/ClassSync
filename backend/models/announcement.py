from datetime import datetime, timezone
from backend import db


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='normal')  # urgent/important/normal
    target_audience = db.Column(db.String(20), nullable=False, default='all')  # all/student/teacher/hod
    target_class = db.Column(db.String(100), nullable=True)
    target_department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reads = db.relationship('AnnouncementRead', backref='announcement', lazy=True, cascade='all, delete-orphan')
    author = db.relationship('User', foreign_keys=[posted_by], backref='announcements_posted')

    def to_dict(self, current_user_id=None):
        from backend.models.user import User
        author = User.query.get(self.posted_by)
        is_read = False
        if current_user_id:
            is_read = AnnouncementRead.query.filter_by(
                announcement_id=self.id, user_id=current_user_id
            ).first() is not None
        read_count = len(self.reads)
        return {
            'id': self.id,
            'posted_by': self.posted_by,
            'author_name': author.name if author else 'Unknown',
            'author_role': author.role if author else '',
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'target_audience': self.target_audience,
            'target_class': self.target_class,
            'target_department': self.target_department,
            'created_at': self.created_at.isoformat(),
            'is_read': is_read,
            'read_count': read_count,
        }


class AnnouncementRead(db.Model):
    __tablename__ = 'announcement_reads'

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('announcement_id', 'user_id', name='uix_ann_user'),
    )


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='general')
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
        }
