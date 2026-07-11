import os
import sys
import traceback

port = int(os.environ.get("PORT", 8080))

# Try to import the full app; fall back to minimal if it fails
app = None
import_error = None

print("=== DEBUG: Python %s on %s ===" % (sys.version.split()[0], sys.platform), file=sys.stderr)
print("=== DEBUG: CWD = %s ===" % os.getcwd(), file=sys.stderr)
print("=== DEBUG: sys.path = %s ===" % sys.path, file=sys.stderr)

# Walk known modules to find the break
for modname in [
    "app.core.config",
    "app.core.logging",
    "app.core.middleware.error_handler",
    "app.core.middleware.request_id",
    "app.core.middleware.request_logger",
    "app.db.mongodb",
    "app.db.supabase",
    "app.infrastructure.cache.redis",
    "app.infrastructure.storage",
    "app.services.ml_service",
    "app.services.receipt_service",
    "app.services.receipt_ocr_v2",
    "app.api.deps",
    "app.services.auth_service",
    "app.api.v1.router",
]:
    try:
        __import__(modname)
        print("IMPORT OK: %s" % modname, file=sys.stderr)
    except Exception as e:
        print("IMPORT FAIL: %s -> %s" % (modname, e), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

try:
    from app.main import app
    print("=== Full app imported OK ===", file=sys.stderr)
except Exception as e:
    import_error = traceback.format_exc()
    print("=== WARN: app.main import failed ===", file=sys.stderr)
    print(import_error, file=sys.stderr)

if app is None:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="IntelliMoney (fallback)")

    @app.get("/healthz")
    @app.get("/api/v1/health")
    async def healthz():
        return JSONResponse({
            "status": "ok",
            "import_error": repr(import_error),
        })

    @app.get("/")
    async def root():
        return {"message": "IntelliMoney API (fallback - app import failed)"}

print("Starting uvicorn on 0.0.0.0:%d" % port, file=sys.stderr)
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
