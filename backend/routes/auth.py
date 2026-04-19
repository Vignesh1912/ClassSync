from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlsplit
from backend import db
from backend.models.user import User, Student, Teacher
from backend.utils.insforge import InsForgeAuth

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'dashboard.{current_user.role}'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        college_user_id = request.form.get('college_user_id', '').strip().upper()
        remember = bool(request.form.get('remember'))
        
        if not college_user_id:
            flash('Please enter your College User ID')
            return redirect(url_for('auth.login'))
        
        # All three must match the SAME user record
        user = User.query.filter_by(email=email, college_user_id=college_user_id).first()
        if user is None or not user.check_password(password):
            flash('Invalid credentials. Email, College User ID and password must all match.')
            return redirect(url_for('auth.login'))
            
        if not user.is_verified:
            flash('Please verify your email address to log in.', 'warning')
            session['verify_email'] = user.email
            return redirect(url_for('auth.verify_email'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for(f'dashboard.{user.role}')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'dashboard.{current_user.role}'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        college_user_id = request.form.get('college_user_id')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role').lower() # student, teacher, hod, admin
        
        # Admin does not belong to a specific department
        if role == 'admin' or not department:
            department = None
        
        if User.query.filter_by(email=email).first():
            flash('Email address already registered')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(college_user_id=college_user_id).first():
            flash('College User ID already registered')
            return redirect(url_for('auth.register'))
            
        user = User(
            name=name, 
            email=email, 
            role=role, 
            department=department, 
            college_user_id=college_user_id,
            is_verified=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # To get user.id before commit
        
        # Optionally create corresponding role profiles
        if role == 'student':
            class_section = request.form.get('class_section')
            student = Student(user_id=user.id, class_section=class_section)
            db.session.add(student)
        elif role == 'teacher':
            teacher = Teacher(user_id=user.id)
            db.session.add(teacher)
            
        db.session.commit()
        
        insauth_resp, insauth_status = InsForgeAuth.register_user(email, password, name)
        if insauth_status >= 400:
            flash(f'Registration failed (Auth): {insauth_resp.get("error", "Unknown error")}', 'error')
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('auth.register'))
            
        InsForgeAuth.send_verification_email(email)
        
        flash('Registration successful! Please check your email for the verification code.', 'success')
        session['verify_email'] = email
        return redirect(url_for('auth.verify_email'))
        
    return render_template('auth/register.html')

@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = session.get('verify_email')
    
    if not email:
        flash('No pending verification found. Please log in.')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        # Send OTP to InsForge to verify
        resp, status = InsForgeAuth.verify_email_otp(email, otp)
        
        if status >= 400:
            error_msg = resp.get('message') or resp.get('error') or 'Invalid code or expired'
            flash(f"Verification failed: {error_msg}", 'error')
            return redirect(url_for('auth.verify_email'))
            
        # Success! Mark user strictly in local DB
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            
            # Clear session cache and log them in
            session.pop('verify_email', None)
            login_user(user)
            flash('Email successfully verified!', 'success')
            return redirect(url_for(f'dashboard.{user.role}'))
            
    return render_template('auth/verify_email.html', email=email)

@bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    email = session.get('verify_email') or request.form.get('email', '').strip().lower()
    if not email:
        flash('No pending verification session found. Please register again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Keep the email in session in case it wasn't there
    session['verify_email'] = email
    
    resp, status = InsForgeAuth.send_verification_email(email)
    if status < 400:
        flash('A new verification code has been sent to your email. Please check your inbox and spam folder.', 'success')
    else:
        flash(f'Failed to resend code: {resp.get("error", "Unknown error")}', 'error')
    return redirect(url_for('auth.verify_email'))
