import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('c:/Users/vigne/classSync/app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM assignment")
        assignment_count = cursor.fetchone()[0]
        print(f"Users in local app.db: {user_count}")
        print(f"Assignments in local app.db: {assignment_count}")
    except Exception as e:
        print(f"Error reading app.db: {e}")

check_db()
