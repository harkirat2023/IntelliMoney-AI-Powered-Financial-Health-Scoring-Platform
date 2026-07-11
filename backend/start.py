import os
import sys
import traceback

port = int(os.environ.get("PORT", 8080))

try:
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(title="IntelliMoney")

    @app.get("/")
    async def root():
        return {"app": "IntelliMoney"}

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
