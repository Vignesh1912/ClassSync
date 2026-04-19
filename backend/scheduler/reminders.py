import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_scheduler = None


def get_scheduler():
    global _scheduler
    return _scheduler


def start_scheduler(app):
    global _scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger

        if _scheduler and _scheduler.running:
            return

        _scheduler = BackgroundScheduler()

        def reminder_job():
            with app.app_context():
                _run_reminders()

        _scheduler.add_job(
            reminder_job,
            trigger=CronTrigger(hour=3, minute=30),  # 3:30 AM UTC = 9:00 AM IST
            id='daily_reminders',
            replace_existing=True
        )
        _scheduler.start()
        logger.info("ClassSync reminder scheduler started.")
    except Exception as exc:
        logger.error("Failed to start scheduler: %s", exc)


def _run_reminders():
    """Check pending submissions and send email reminders where appropriate."""
    try:
        from backend import db
        from backend.models.assignment import Submission, Assignment, NotificationPrefs
        from backend.models.user import Student, User
        from backend.utils.email import send_reminder_email

        today = datetime.utcnow().date()
        pending = Submission.query.filter_by(status='pending').all()

        for sub in pending:
            assignment = Assignment.query.get(sub.assignment_id)
            if not assignment:
                continue

            deadline_date = assignment.deadline.date()
            days_remaining = (deadline_date - today).days

            if days_remaining not in (3, 2, 1, 0):
                continue

            student = Student.query.get(sub.student_id)
            if not student:
                continue
            user = student.user
            if not user:
                continue

            prefs = NotificationPrefs.query.filter_by(user_id=user.id).first()
            if prefs is None:
                # Default: send all reminders
                prefs_email_enabled = True
                day_pref = True
            else:
                prefs_email_enabled = prefs.email_enabled
                day_map = {3: prefs.remind_3days, 2: prefs.remind_2days,
                           1: prefs.remind_1day, 0: prefs.remind_deadline}
                day_pref = day_map.get(days_remaining, False)

            if prefs_email_enabled and day_pref:
                send_reminder_email(
                    student_email=user.email,
                    student_name=user.name,
                    assignment_title=assignment.title,
                    deadline=assignment.deadline,
                    days_remaining=days_remaining,
                    classroom_link=assignment.classroom_link
                )

    except Exception as exc:
        logger.error("Reminder job failed: %s", exc)
