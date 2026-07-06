#!/usr/bin/env python3
"""
IntelliMoney - Single file to start all services
Starts: MongoDB check, Backend (FastAPI), Frontend (Vite)
"""

import subprocess
import sys
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
ML_MODEL_PATH = BACKEND_DIR / "app" / "ml" / "expense_classifier.joblib"


def run_command(cmd, cwd=None, shell=True, check=True):
    """Run a command and stream output."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"Directory: {cwd or ROOT}")
    print(f"{'='*60}\n")
    
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Stream output in real-time
    for line in process.stdout:
        print(line, end='', flush=True)
    
    process.wait()
    if check and process.returncode != 0:
        print(f"\n❌ Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)
    
    return process.returncode


def check_mongodb():
    """Check if MongoDB is running."""
    print("\n🔍 Checking MongoDB connection...")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from pymongo import MongoClient
        from app.core.config import get_settings
        
        settings = get_settings()
        client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB check failed: {e}")
        print("💡 Make sure MongoDB is installed and running.")
        print("   - Local: Start MongoDB service")
        print("   - Atlas: Check your connection string in backend/.env")
        return False


def check_ml_model():
    """Check if ML model exists, if not train it."""
    if ML_MODEL_PATH.exists():
        print(f"\n✅ ML model found at: {ML_MODEL_PATH}")
        return
    
    print(f"\n⚠️  ML model not found at: {ML_MODEL_PATH}")
    print("🤖 Training ML model...")
    run_command("python ml/train_model.py", cwd=ROOT)
    print("✅ ML model trained successfully")


def install_backend_deps():
    """Install backend dependencies if needed."""
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print("❌ Backend requirements.txt not found")
        sys.exit(1)
    
    print("\n📦 Checking backend dependencies...")
    # Try to import fastapi to check if deps are installed
    try:
        import fastapi
        print("✅ Backend dependencies already installed")
    except ImportError:
        print("📥 Installing backend dependencies...")
        run_command(f'pip install -r "{requirements_file}"', cwd=ROOT)


def install_frontend_deps():
    """Install frontend dependencies if needed."""
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists():
        print("\n✅ Frontend dependencies already installed")
        return
    
    print("\n📦 Installing frontend dependencies...")
    run_command("npm install", cwd=FRONTEND_DIR)


def start_backend():
    """Start the FastAPI backend server."""
    BACKEND_PORT = 8080  # Changed from 8000 to avoid conflicts
    print(f"\n🚀 Starting FastAPI backend...")
    print(f"📍 Backend will run at: http://localhost:{BACKEND_PORT}")
    print(f"📚 API docs at: http://localhost:{BACKEND_PORT}/docs\n")
    
    # Use subprocess.Popen to keep it running
    process = subprocess.Popen(
        f'uvicorn app.main:app --reload --host 0.0.0.0 --port {BACKEND_PORT}',
        cwd=BACKEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Give it more time to start (increased from 3 to 5 seconds)
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is not None:
        print("❌ Backend failed to start")
        sys.exit(1)
    
    print("✅ Backend started successfully")
    return process


def start_frontend():
    """Start the Webpack frontend dev server."""
    print("\n🎨 Starting Webpack frontend...")
    print("📍 Frontend will run at: http://localhost:5173\n")
    
    process = subprocess.Popen(
        "npm run dev",
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Give it more time to start (increased from 3 to 5 seconds)
    print("⏳ Waiting for frontend to initialize...")
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is not None:
        print("❌ Frontend failed to start")
        sys.exit(1)
    
    print("✅ Frontend started successfully")
    return process


def main():
    print("="*60)
    print("💰 IntelliMoney - Starting All Services")
    print("="*60)
    
    # Pre-flight checks
    check_ml_model()
    install_backend_deps()
    install_frontend_deps()
    
    # Check MongoDB (warning only, don't block)
    mongodb_ok = check_mongodb()
    if not mongodb_ok:
        print("\n⚠️  Continuing without MongoDB... Backend may fail to connect.")
    
    # Start services
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    print("\n" + "="*60)
    print("✅ All services started successfully!")
    print("="*60)
    BACKEND_PORT = 8080
    print("\n📍 Services running:")
    print(f"   - Backend:  http://localhost:{BACKEND_PORT}")
    print("   - Frontend: http://localhost:5173")
    print(f"   - API Docs: http://localhost:{BACKEND_PORT}/docs")
    print("\n💡 Press Ctrl+C to stop all services\n")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
    finally:
        # Cleanup
        print("Cleaning up...")
        for proc in [backend_process, frontend_process]:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        
        print("✅ All services stopped")
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()