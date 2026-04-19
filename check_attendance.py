import sqlite3
conn = sqlite3.connect('app.db')

# Find Vignesh's student ID
stu = conn.execute("SELECT s.id FROM students s JOIN users u ON s.user_id=u.id WHERE u.college_user_id='STU-1255'").fetchone()
print('Student ID:', stu)

if stu:
    sid = stu[0]
    rows = conn.execute('''
        SELECT sub.subject_code, sub.subject_name,
               COUNT(a.id) as attended,
               (SELECT COUNT(*) FROM attendance_sessions WHERE subject_id=asess.subject_id) as total
        FROM attendance a
        JOIN attendance_sessions asess ON a.session_id=asess.id
        JOIN subjects sub ON asess.subject_id=sub.id
        WHERE a.student_id=? AND a.status='present'
        GROUP BY asess.subject_id
    ''', (sid,)).fetchall()
    for r in rows:
        attended, total = r[2], r[3]
        pct = round(attended/total*100, 1) if total else 0
        print(f'{r[0]} - {r[1]}: {attended}/{total} = {pct}% | at_risk: {pct < 75}')

conn.close()
