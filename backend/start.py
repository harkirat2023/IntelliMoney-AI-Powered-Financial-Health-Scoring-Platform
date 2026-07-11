import os
import sys
import traceback

print("=== IntelliMoney Startup ===", file=sys.stderr)
print(f"Python: {sys.version}", file=sys.stderr)
print(f"CWD: {os.getcwd()}", file=sys.stderr)
print(f"PORT: {os.environ.get('PORT', 'not set')}", file=sys.stderr)
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'not set')}", file=sys.stderr)

try:
    print("Step 1: Importing uvicorn...", file=sys.stderr)
    import uvicorn
    print("Step 2: Importing app.main...", file=sys.stderr)
    from app.main import app
    print("Step 3: Starting uvicorn...", file=sys.stderr)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120)
except Exception:
    print("=== STARTUP FAILED ===", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
