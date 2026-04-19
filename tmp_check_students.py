import sqlite3
import json

conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# All students with user check
cursor.execute("SELECT * FROM students ORDER BY id")
students = [dict(r) for r in cursor.fetchall()]
print("All Students in SQLite:")
for s in students:
    print(f"  student.id={s['id']} user_id={s['user_id']} roll={s['roll_number']} section={s['class_section']}")

# Check user 22 exists
cursor.execute("SELECT id, name, college_user_id FROM users WHERE id = 22")
u22 = cursor.fetchone()
print(f"\nUser id=22: {dict(u22) if u22 else 'NOT FOUND'}")

# Check users in export JSON
with open('tmp_db_export.json') as f:
    data = json.load(f)
user_ids_in_export = [u['id'] for u in data['users']]
print(f"\nUser IDs in export: {sorted(user_ids_in_export)}")
print(f"Student user_ids: {[s['user_id'] for s in students]}")
print(f"Missing from export: {[uid for uid in [s['user_id'] for s in students] if uid not in user_ids_in_export]}")

conn.close()
