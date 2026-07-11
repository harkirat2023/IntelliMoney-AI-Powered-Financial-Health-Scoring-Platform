import os
import sys
import traceback

port = int(os.environ.get("PORT", 8080))

app = None

try:
    from app.main import app
except Exception:
    traceback.print_exc(file=sys.stderr)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="IntelliMoney (fallback)")
    error = traceback.format_exc()

    @app.get("/healthz")
    @app.get("/api/v1/health")
    async def healthz():
        return JSONResponse({"status": "error", "import_error": error})

    @app.get("/")
    async def root():
        return {"message": "IntelliMoney API (fallback)"}

import uvicorn
try:
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
