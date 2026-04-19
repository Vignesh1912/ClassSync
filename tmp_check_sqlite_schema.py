import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(students)")
print("LOCAL SQLITE STUDENTS SCHEMA:")
for r in cursor.fetchall():
    print(r)
