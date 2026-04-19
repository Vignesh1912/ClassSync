import os
with open('c:\\Users\\vigne\\classSync\\tmp_env_dump.txt', 'w') as f:
    for k, v in os.environ.items():
        if 'DATABASE' in k.upper() or 'INSFORGE' in k.upper() or 'POSTGRES' in k.upper():
            f.write(f"{k}={v}\n")
print("Dumped environment targeting DB keys.")
