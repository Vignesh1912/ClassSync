import sqlite3

try:
    with sqlite3.connect('c:\\Users\\vigne\\classSync\\app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
        with open('c:\\Users\\vigne\\classSync\\tmp_schema_dump.txt', 'w') as f:
            for row in cursor.fetchall():
                if row[0]:
                    f.write(row[0] + ";\n\n")
    print("Schema dumped into tmp_schema_dump.txt")
except Exception as e:
    print(f"Error: {e}")
