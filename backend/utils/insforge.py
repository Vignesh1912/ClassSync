import requests
from flask import current_app

class InsForgeAuth:
    """
    A utility wrapper for interacting with the InsForge REST API for authentication.
    """
    
    @classmethod
    def get_headers(cls):
        url = current_app.config.get('INSFORGE_URL')
        key = current_app.config.get('INSFORGE_ANON_KEY')
        if not url or not key:
            raise ValueError("InsForge credentials are not configured properly.")
        
        return {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }

    @classmethod
    def get_base_url(cls):
        url = current_app.config.get('INSFORGE_URL')
        if not url:
            raise ValueError("InsForge URL is missing.")
        return f"{url.rstrip('/')}/api/auth"

    @classmethod
    def register_user(cls, email, password, name=None):
        """
        Creates a new user account in InsForge.
        """
        url = f"{cls.get_base_url()}/users"
        payload = {
            "email": email,
            "password": password
        }
        if name:
            payload["name"] = name
            
        try:
            response = requests.post(url, json=payload, headers=cls.get_headers())
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500

    @classmethod
    def send_verification_email(cls, email):
        """
        Triggers InsForge to dispatch the 6-digit OTP verification email.
        """
        url = f"{cls.get_base_url()}/email/send-verification"
        payload = {"email": email}
        
        try:
            response = requests.post(url, json=payload, headers=cls.get_headers())
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500

    @classmethod
    def verify_email_otp(cls, email, otp):
        """
        Submits the 6-digit OTP to InsForge to verify the user's email.
        """
        url = f"{cls.get_base_url()}/email/verify"
        payload = {
            "email": email,
            "otp": otp
        }
        
        try:
            response = requests.post(url, json=payload, headers=cls.get_headers())
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500
