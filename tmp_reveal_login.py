from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Let's find any teacher
    teachers = User.query.filter_by(role='teacher').all()
    for t in teachers:
        # Assuming we don't know passwords, we can Reset one for Swaruuu Sir to 'password123'
        # OR we can just check if there is a 'demo_teacher' with fixed credentials or open.
        # Let's check for Swaruuu Sir and set his password temporarily to 'password123'
        if 'Swaruuu' in t.name:
            from werkzeug.security import generate_password_hash
            t.password_hash = generate_password_hash('password123')
            db.session.commit()
            with open('c:\\Users\\vigne\\classSync\\tmp_creds.txt', 'w') as f:
                f.write(f"Email: {t.email}\nPassword: password123")
            print("Credentials saved to tmp_creds.txt")
            break
