import logging
from datetime import datetime, timezone

from backend.utils.email import send_email

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from backend import db
from backend.models.announcement import Announcement, AnnouncementRead, Notification
from backend.models.user import User, Student

bp = Blueprint('announcement', __name__)
logger = logging.getLogger(__name__)


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_targeted_users(target_audience, target_class, target_department):
    """Return list of User objects matching the targeting criteria."""
    query = User.query.filter_by(is_active=True)
    if target_audience != 'all':
        query = query.filter_by(role=target_audience)
    users = query.all()

    result = []
    for u in users:
        if target_class:
            prof = u.student_profile
            if not prof or prof.class_section != target_class:
                continue
        if target_department and u.department != target_department:
            continue
        result.append(u)
    return result


def _announcement_visible(ann, user):
    """Return True if this announcement should be visible to `user`."""
    if user.role == 'admin':
        return True
    ta = ann.target_audience
    if ta == 'all':
        return True
    if ta == user.role:
        return True
    # target_class match for students
    if ann.target_class and user.student_profile and \
            user.student_profile.class_section == ann.target_class:
        return True
    # department match
    if ann.target_department and user.department == ann.target_department:
        return True
    return False


def _send_urgent_emails(announcement, users):
    """Best-effort urgent email via smtplib (configured via MAIL_* env vars)."""
    author_name = announcement.author.name if announcement.author else 'Admin'
    author_role = announcement.author.role if announcement.author else ''
    subject = f"URGENT: {announcement.title}"
    body = (
        f"URGENT ANNOUNCEMENT from ClassSync\n\n"
        f"{announcement.content}\n\n"
        f"— Posted by {author_name} ({author_role})\n"
        f"\nLog in to ClassSync to view the full announcement."
    )
    for u in users:
        try:
            send_email(u.email, subject, body)
        except Exception as exc:
            logger.warning("Urgent email failed for %s: %s", u.email, exc)


# ── page routes ───────────────────────────────────────────────────────────────

@bp.route('/announcements')
@login_required
def announcements_page():
    return render_template('announcements/index.html', title='Announcements')


# /notifications page removed per user request


# ── API: create announcement ──────────────────────────────────────────────────

@bp.route('/api/announcements/create', methods=['POST'])
@login_required
def api_create_announcement():
    if current_user.role not in ('admin', 'hod', 'teacher'):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    priority = data.get('priority', 'normal').lower()
    target_audience = data.get('target_audience', 'all')
    target_class = data.get('target_class', '').strip() or None
    target_department = data.get('target_department', '').strip() or None

    if not title or not content:
        return jsonify({'error': 'title and content are required'}), 400

    if priority not in ('urgent', 'important', 'normal'):
        return jsonify({'error': 'Invalid priority'}), 400

    if priority == 'urgent' and current_user.role == 'teacher':
        return jsonify({'error': 'Teachers cannot post urgent announcements'}), 403

    ann = Announcement(
        posted_by=current_user.id,
        title=title,
        content=content,
        priority=priority,
        target_audience=target_audience,
        target_class=target_class,
        target_department=target_department,
    )
    db.session.add(ann)
    db.session.flush()

    # Determine targeted users for in-app notifications (and emails if urgent)
    targeted_users = _get_targeted_users(target_audience, target_class, target_department)

    for u in targeted_users:
        if u.id == current_user.id:
            continue  # don't notify yourself
        notif = Notification(
            user_id=u.id,
            type='announcement',
            title=f"{'🔴 URGENT: ' if priority == 'urgent' else ''}{title}",
            message=content[:200] + ('…' if len(content) > 200 else ''),
        )
        db.session.add(notif)

    db.session.commit()

    if priority == 'urgent':
        _send_urgent_emails(ann, [u for u in targeted_users if u.id != current_user.id])

    return jsonify(ann.to_dict(current_user_id=current_user.id)), 201


# ── API: list announcements ───────────────────────────────────────────────────

@bp.route('/api/announcements/list', methods=['GET'])
@login_required
def api_list_announcements():
    priority_filter = request.args.get('priority')

    all_anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    visible = [a for a in all_anns if _announcement_visible(a, current_user)]

    if priority_filter:
        visible = [a for a in visible if a.priority == priority_filter]

    # Sort: urgent first (newest→oldest), then important, then normal
    order = {'urgent': 0, 'important': 1, 'normal': 2}
    visible.sort(key=lambda a: (order.get(a.priority, 9),
                                 -a.created_at.timestamp()))

    return jsonify([a.to_dict(current_user_id=current_user.id) for a in visible])


# ── API: unread count ─────────────────────────────────────────────────────────

@bp.route('/api/announcements/unread-count', methods=['GET'])
@login_required
def api_unread_count():
    all_anns = Announcement.query.all()
    visible_ids = [a.id for a in all_anns if _announcement_visible(a, current_user)]
    read_ids = {r.announcement_id for r in
                AnnouncementRead.query.filter_by(user_id=current_user.id).all()}
    count = sum(1 for aid in visible_ids if aid not in read_ids)
    return jsonify({'count': count})


# ── API: mark read ────────────────────────────────────────────────────────────

@bp.route('/api/announcements/mark-read/<int:ann_id>', methods=['POST'])
@login_required
def api_mark_read(ann_id):
    existing = AnnouncementRead.query.filter_by(
        announcement_id=ann_id, user_id=current_user.id
    ).first()
    if not existing:
        rec = AnnouncementRead(announcement_id=ann_id, user_id=current_user.id)
        db.session.add(rec)
        db.session.commit()
    return jsonify({'success': True})


# ── API: read receipts ────────────────────────────────────────────────────────

@bp.route('/api/announcements/read-receipts/<int:ann_id>', methods=['GET'])
@login_required
def api_read_receipts(ann_id):
    if current_user.role not in ('admin', 'hod'):
        return jsonify({'error': 'Unauthorized'}), 403
    reads = AnnouncementRead.query.filter_by(announcement_id=ann_id).all()
    result = []
    for r in reads:
        u = User.query.get(r.user_id)
        result.append({
            'name': u.name if u else 'Unknown',
            'role': u.role if u else '',
            'read_at': r.read_at.isoformat(),
        })
    return jsonify(result)


# ── API: delete announcement ──────────────────────────────────────────────────

@bp.route('/api/announcements/delete/<int:ann_id>', methods=['DELETE'])
@login_required
def api_delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    # Only the poster or admin/hod can delete
    if ann.posted_by != current_user.id and current_user.role not in ('admin', 'hod'):
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(ann)
    db.session.commit()
    return jsonify({'success': True})


# ── API: notifications list ───────────────────────────────────────────────────

@bp.route('/api/notifications/list', methods=['GET'])
@login_required
def api_notifications_list():
    notifs = (Notification.query
              .filter_by(user_id=current_user.id)
              .order_by(Notification.created_at.desc())
              .all())
    return jsonify([n.to_dict() for n in notifs])


@bp.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def api_notifications_unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


# ── API: mark all notifications read ─────────────────────────────────────────

@bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def api_notifications_mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {'is_read': True}
    )
    db.session.commit()
    return jsonify({'success': True})
