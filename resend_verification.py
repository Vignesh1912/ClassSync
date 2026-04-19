from backend import create_app
from backend.utils.insforge import InsForgeAuth

app = create_app()
with app.app_context():
    email = 'sanskrutibathe2211@gmail.com'
    print(f"Resending verification email to {email}...")
    resp, status = InsForgeAuth.send_verification_email(email)
    print(f"Status: {status}")
    print(f"Response: {resp}")
