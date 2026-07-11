import json, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

entries = data.get("value", [])
print(f"Log entries: {len(entries)}")
for e in entries[:20]:
    print(json.dumps(e, indent=2)[:300])
