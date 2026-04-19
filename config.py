import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session lifetime
    from datetime import timedelta
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # InsForge
    INSFORGE_URL = os.environ.get('INSFORGE_URL')
    INSFORGE_ANON_KEY = os.environ.get('INSFORGE_ANON_KEY')

    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf'}

    # Resend — transactional email (urgent announcements + assignment reminders)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')

