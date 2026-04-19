import json

with open('tmp_db_export.json') as f:
    data = json.load(f)

print("Students in export:")
for s in data['students']:
    print(f"  {s}")

print("\nFirst student INSERT would be:")
s = data['students'][0]
cols = ', '.join(s.keys())
vals_list = []
for v in s.values():
    if v is None:
        vals_list.append('NULL')
    elif isinstance(v, bool):
        vals_list.append('TRUE' if v else 'FALSE')
    elif isinstance(v, (int, float)):
        vals_list.append(str(v))
    else:
        vals_list.append("'" + str(v).replace("'", "''") + "'")
vals = ', '.join(vals_list)
print(f"INSERT INTO students ({cols}) VALUES ({vals}) ON CONFLICT DO NOTHING")
