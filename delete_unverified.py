import sqlite3
conn = sqlite3.connect('app.db')

# Get IDs of unverified users
ids = [r[0] for r in conn.execute('SELECT id FROM users WHERE is_verified=0').fetchall()]
print('Deleting user IDs:', ids)

if ids:
    placeholders = ','.join('?' * len(ids))
    conn.execute(f'DELETE FROM students WHERE user_id IN ({placeholders})', ids)
    conn.execute(f'DELETE FROM teachers WHERE user_id IN ({placeholders})', ids)
    conn.execute('DELETE FROM users WHERE is_verified=0')
    conn.commit()
    print(f'Done! Deleted {len(ids)} unverified users.')
else:
    print('No unverified users found.')

conn.close()
