"""
Quick smoke test: send a test email via Resend API.
Run: python test_resend.py
"""
import requests

API_KEY = 're_Rn2jxVdN_M5G7aS8M9rGW1DdpnA5AU9Yo'
TO_EMAIL = 'vigneshvickysvk@gmail.com'

resp = requests.post(
    'https://api.resend.com/emails',
    headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    },
    json={
        'from': 'ClassSync <onboarding@resend.dev>',
        'to': [TO_EMAIL],
        'subject': '[ClassSync] Email Test — Resend working!',
        'text': (
            'Hi Vignesh,\n\n'
            'This is a test email from ClassSync to confirm Resend is set up correctly.\n\n'
            'Urgent announcement emails and assignment reminders will now be delivered to this address.\n\n'
            '— ClassSync'
        ),
    },
    timeout=15,
)

print(f'Status : {resp.status_code}')
print(f'Response: {resp.text}')
if resp.ok:
    print('\n✅ Email sent successfully! Check your inbox.')
else:
    print('\n❌ Failed. Check the error above.')
