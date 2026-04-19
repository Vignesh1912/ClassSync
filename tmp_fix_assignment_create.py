path = 'c:\\Users\\vigne\\classSync\\app\\routes\\assignment.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We know Chunk 0 (line 64) is fixed because of the successful diff. 
# Only the api_create_assignment at line 108 remained.
target = "if current_user.role not in ('teacher', 'hod', 'admin'):"
replace = "if current_user.role not in ('teacher', 'hod'):"

if content.count(target) > 0:
    content = content.replace(target, replace)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Target NOT found in file.")
