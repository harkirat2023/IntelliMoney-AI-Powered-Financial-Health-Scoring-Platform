import sys, json

data = json.load(sys.stdin)
events = data if isinstance(data, list) else data.get("value", [])
for e in events[:5]:
    if isinstance(e, dict) and "event" in e:
        ev = e["event"]
    else:
        ev = e
    typ = ev.get("type", "")
    details = ev.get("details", {})
    status = details.get("deployStatus", "")
    reason = details.get("reason", {})
    failure = reason.get("failure", {})
    exit_code = failure.get("nonZeroExit", "")
    print(f"{typ} | status={status} | exit={exit_code}")

print(f"\nTotal events: {len(events)}")
