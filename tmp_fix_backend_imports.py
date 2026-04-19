import os

directory_to_scan = 'c:\\Users\\vigne\\classSync\\backend'

def fix_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    targets = [
        ("from app import", "from backend import"),
        ("from app.models", "from backend.models"),
        ("from app.routes", "from backend.routes"),
        ("from app.utils", "from backend.utils"),
        ("from app.scheduler", "from backend.scheduler")
    ]
    
    for t, r in targets:
        if t in content:
            content = content.replace(t, r)
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")

for root, dirs, files in os.walk(directory_to_scan):
    for file in files:
        if file.endswith('.py'):
            fix_imports_in_file(os.path.join(root, file))

print("Global import replacement batch finished.")
