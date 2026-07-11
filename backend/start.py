import os
import sys
import traceback

port = int(os.environ.get("PORT", 8080))

try:
    import uvicorn

    print("Importing main app...", file=sys.stderr)
    from app.main import app
    print("App imported successfully", file=sys.stderr)

    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
