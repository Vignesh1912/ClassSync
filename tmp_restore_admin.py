path = 'c:\\Users\\vigne\\classSync\\app\\routes\\assignment.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore role checks
content = content.replace(
    "if current_user.role not in ('teacher', 'hod'):",
    "if current_user.role not in ('teacher', 'hod', 'admin'):"
)

# 2. Restore Admin subjects fallback
target_form = """    if current_user.role not in ('teacher', 'hod', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    subjects = Subject.query.filter_by(department=current_user.department).all()"""

replace_form = """    if current_user.role not in ('teacher', 'hod', 'admin'):
        flash('Access denied')
        return redirect(url_for('dashboard.index'))
    if current_user.role == 'admin':
        subjects = Subject.query.all()
    else:
        subjects = Subject.query.filter_by(department=current_user.department).all()"""

if target_form in content:
    content = content.replace(target_form, replace_form)
    print("Subjects fallback restored.")
else:
    print("Subjects fallback line not matched. Will check again.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored Admin Role checks.")
