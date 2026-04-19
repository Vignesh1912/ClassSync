import sqlite3
def check_db():
    conn = sqlite3.connect('c:/Users/vigne/classSync/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
check_db()
