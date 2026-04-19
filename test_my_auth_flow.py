import requests

data = {
    'name': 'Test AI Run',
    'email': 'testing_email_flow_99@example.com',
    'department': 'CSE',
    'college_user_id': 'STU-9900',
    'password': 'Password123!',
    'confirm_password': 'Password123!',
    'role': 'Student',
    'class_section': 'Semester 4 - CSE Alpha',
    'terms': 'on'
}

req = requests.post('http://127.0.0.1:5000/register', data=data, allow_redirects=False)
print("Registration POST Status:", req.status_code)
print("Redirected to:", req.headers.get('Location'))
