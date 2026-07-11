import os
import sys
import traceback

IMPORTS = [
    "fastapi",
    "app.core.config",
    "app.core.logging",
    "app.core.middleware.error_handler",
    "app.core.middleware.request_id",
    "app.core.middleware.request_logger",
    "app.db.mongodb",
    "app.infrastructure.cache.redis",
    "app.services.ml_service",
]

for mod in IMPORTS:
    try:
        __import__(mod)
        print(f"OK: {mod}", file=sys.stderr)
    except Exception as e:
        print(f"FAIL: {mod}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

print("Importing app.main...", file=sys.stderr)
try:
    from app.main import app
    print("Import OK", file=sys.stderr)
except Exception as e:
    print(f"FAIL: app.main: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

port = int(os.environ.get("PORT", 8080))
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
