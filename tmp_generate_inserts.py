import sqlite3
import json

tables_order = [
    'users', 'subjects', 'students', 'teachers', 'timetable', 
    'attendance_sessions', 'attendance', 'session_activity_log', 
    'notification_prefs', 'assignments', 'submissions', 
    'announcements', 'notifications', 'announcement_reads'
]

def quote(v):
    if v is None:
        return 'NULL'
    if isinstance(v, str):
        # escape single quotes
        safe_v = v.replace("'", "''")
        return f"'{safe_v}'"
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    return str(v)

try:
    with sqlite3.connect('c:\\Users\\vigne\\classSync\\app.db') as conn:
        cursor = conn.cursor()
        with open('c:\\Users\\vigne\\classSync\\tmp_inserts.sql', 'w', encoding='utf-8') as f:
            for table in tables_order:
                # get columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                cols_str = ", ".join(columns)
                
                # get rows
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if rows:
                    f.write(f"-- Data for {table}\n")
                    for row in rows:
                        vals_str = ", ".join(quote(v) for v in row)
                        f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});\n")
                    
                    # Add Sequence Updates for PostgreSQL
                    f.write(f"SELECT setval('{table}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table}));\n\n")
                    
    print("Inserts generated into tmp_inserts.sql")
except Exception as e:
    print(f"Error: {e}")
