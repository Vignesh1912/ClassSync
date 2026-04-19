from backend import create_app
from backend.utils.insforge import InsForgeAuth
app = create_app()
with app.app_context():
    print("Testing InsForge Register...")
    resp, code = InsForgeAuth.register_user("test.registration3@example.com", "Password123!", "Test User")
    print(code, resp)
