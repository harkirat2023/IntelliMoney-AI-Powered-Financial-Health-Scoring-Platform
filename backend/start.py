import os
import sys
import traceback

# Print startup info to stderr (Render captures this)
print("=== IntelliMoney Startup ===", file=sys.stderr)
print(f"Python: {sys.version}", file=sys.stderr)
print(f"CWD: {os.getcwd()}", file=sys.stderr)
print(f"PATH: {os.environ.get('PATH', '')[:200]}", file=sys.stderr)
print(f"PORT: {os.environ.get('PORT', 'not set')}", file=sys.stderr)

try:
    import uvicorn
    print("uvicorn imported", file=sys.stderr)

    from app.main import app
    print("app imported", file=sys.stderr)

    port = int(os.environ.get("PORT", 8080))
    print(f"Starting uvicorn on port {port}", file=sys.stderr)

    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=120, log_level="debug")
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
