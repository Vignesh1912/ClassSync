import sqlite3
from backend import create_app, db
from backend.models.user import Subject

def migrate_and_seed():
    app = create_app()
    with app.app_context():
        conn = sqlite3.connect('c:/Users/vigne/classSync/app.db')
        cursor = conn.cursor()
        
        # 1. Add class_section if it does not exist
        try:
            cursor.execute("ALTER TABLE attendance_sessions ADD COLUMN class_section VARCHAR(50) DEFAULT NULL")
            print("Successfully added class_section column to attendance_sessions")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("class_section column already exists in attendance_sessions")
            else:
                print(f"Error altering table: {e}")
        
        conn.commit()
        conn.close()

        # 2. Seed Subjects
        subjects_to_add = [
            {'code': 'CS201', 'name': 'Operating Systems', 'cred': 4, 'sem': 3, 'dept': 'CSE'},
            {'code': 'CS202', 'name': 'Database Management Systems', 'cred': 4, 'sem': 3, 'dept': 'CSE'},
            {'code': 'CS301', 'name': 'Computer Networks', 'cred': 3, 'sem': 4, 'dept': 'CSE'},
            {'code': 'EE101', 'name': 'Basic Electronics', 'cred': 3, 'sem': 2, 'dept': 'ENTC'},
            {'code': 'ME205', 'name': 'Engineering Mechanics', 'cred': 4, 'sem': 2, 'dept': 'Mechanical'},
            {'code': 'MBA-HCM', 'name': 'Healthcare Management', 'cred': 3, 'sem': 1, 'dept': 'MBA'}
        ]
        
        added = 0
        for s in subjects_to_add:
            existing = Subject.query.filter_by(subject_code=s['code']).first()
            if not existing:
                new_sub = Subject(
                    subject_code=s['code'],
                    subject_name=s['name'],
                    credits=s['cred'],
                    semester=s['sem'],
                    department=s['dept']
                )
                db.session.add(new_sub)
                added += 1
        
        if added > 0:
            db.session.commit()
            print(f"Added {added} new subjects to the database.")
        else:
            print("All subjects already present in database.")

if __name__ == '__main__':
    migrate_and_seed()
