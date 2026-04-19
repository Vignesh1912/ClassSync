from backend import create_app
from backend.utils.insforge import InsForgeAuth

app = create_app()
with app.app_context():
    email = 'sanskrutibathe2211@gmail.com'
    # Test with a dummy OTP to see the exact error message from InsForge
    resp, status = InsForgeAuth.verify_email_otp(email, '000000')
    print(f"Status: {status}")
    print(f"Response: {resp}")
    
    # Also check what the base URL resolves to
    print(f"\nBase URL: {InsForgeAuth.get_base_url()}")
    print(f"Verify endpoint: {InsForgeAuth.get_base_url()}/email/verify")
