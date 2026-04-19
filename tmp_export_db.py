"""
Export SQLite data to JSON, correctly converting 0/1 integer columns
that are actually BOOLEAN in the PostgreSQL schema to True/False.
"""
import sqlite3
import json

# Map of table -> set of boolean column names (matching the PG schema)
BOOL_COLS = {
    'users':              {'is_verified', 'is_active'},
    'students':           set(),
    'teachers':           set(),
    'subjects':           set(),
    'timetable':          {'is_active'},
    'attendance_sessions': set(),
    'attendance':         {'is_valid'},
    'session_activity_log': set(),
    'notification_prefs': {'email_enabled', 'remind_3days', 'remind_2days', 'remind_1day', 'remind_deadline'},
    'assignments':        set(),
    'submissions':        {'self_reported'},
    'announcements':      set(),
    'notifications':      {'is_read'},
    'announcement_reads': set(),
}

ORDER = [
    'users', 'subjects', 'students', 'teachers', 'timetable',
    'attendance_sessions', 'attendance', 'session_activity_log',
    'notification_prefs', 'assignments', 'submissions',
    'announcements', 'notifications', 'announcement_reads'
]

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

data = {}

for table in ORDER:
    bool_cols = BOOL_COLS.get(table, set())
    cursor.execute(f'SELECT * FROM "{table}"')
    rows = []
    for r in cursor.fetchall():
        row = dict(r)
        for col in bool_cols:
            if col in row and row[col] is not None:
                row[col] = bool(row[col])   # 0 -> False, 1 -> True
        rows.append(row)
    data[table] = rows
    print(f'{table}: {len(rows)} rows (bool cols: {bool_cols or "none"})')

with open('tmp_db_export.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

print('\nExported to tmp_db_export.json (booleans fixed)')
conn.close()
