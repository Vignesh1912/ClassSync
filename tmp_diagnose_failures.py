"""
Diagnose the 3 root failures and generate the exact fix SQL needed.
"""
import sqlite3, json

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Find the user whose password_hash > 128 chars
cursor.execute("SELECT id, college_user_id, name, LENGTH(password_hash) as plen FROM users WHERE LENGTH(password_hash) > 128")
long_pw_users = [dict(r) for r in cursor.fetchall()]
print("=== Users with password_hash > 128 chars ===")
for u in long_pw_users:
    print(f"  id={u['id']} {u['college_user_id']} | {u['name']} | hash_len={u['plen']}")

# 2. Find timetable class_section > 20 chars
cursor.execute("SELECT id, class_section, LENGTH(class_section) as clen FROM timetable WHERE LENGTH(class_section) > 20")
long_sections = [dict(r) for r in cursor.fetchall()]
print("\n=== Timetable rows with class_section > 20 chars ===")
for r in long_sections:
    print(f"  id={r['id']} | '{r['class_section']}' (len={r['clen']})")

# Max class_section length anywhere
cursor.execute("SELECT MAX(LENGTH(class_section)) FROM timetable")
max_t = cursor.fetchone()[0]
cursor.execute("SELECT MAX(LENGTH(class_section)) FROM attendance_sessions")
max_a = cursor.fetchone()[0]
print(f"\n  Max class_section in timetable: {max_t}")
print(f"  Max class_section in attendance_sessions: {max_a}")

# 3. Find which students failed (FK from a user that failed)
cursor.execute("SELECT id, user_id FROM students")
students = [dict(r) for r in cursor.fetchall()]
print("\n=== All students ===")
for s in students:
    print(f"  student.id={s['id']} user_id={s['user_id']}")

conn.close()
