from app import create_app, db
from app.models.user import User, Student, Teacher

app = create_app()
with app.app_context():
    users = User.query.filter_by(email='666thedarkshop@gmail.com').all()
    if not users:
        print("No user found with email 666thedarkshop@gmail.com")
    else:
        for u in users:
            print(f"DELETING: ID={u.id} | Name={u.name} | Email={u.email}")
            Student.query.filter_by(user_id=u.id).delete()
            Teacher.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
        db.session.commit()
        print("Deletion committed successfully!")
