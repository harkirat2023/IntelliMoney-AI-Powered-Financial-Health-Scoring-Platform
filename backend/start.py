import os
import sys
import traceback

port = int(os.environ.get("PORT", 8080))

try:
    from app.main import app
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
