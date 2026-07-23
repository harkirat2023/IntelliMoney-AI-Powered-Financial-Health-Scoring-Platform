@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0.."
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

set "ESC="
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "CYAN=%ESC%[36m"
set "BOLD=%ESC%[1m"
set "RESET=%ESC%[0m"

set "PASS=%GREEN%[PASS]%RESET%"
set "WARN=%YELLOW%[WARN]%RESET%"
set "FAIL=%RED%[FAIL]%RESET%"
set "INFO=%CYAN%[INFO]%RESET%"

echo.& echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney - One-Click Startup%RESET%
echo %BOLD%======================================================%RESET%
echo.

:: ---------- check prerequisites ----------
call :check_prereqs
if errorlevel 1 (
  echo %FAIL% Prerequisites missing. Aborting.
  pause
  exit /b 1
)

:: ---------- detect Docker ----------
set "DOCKER_AVAILABLE=0"
where docker >nul 2>&1 && docker info >nul 2>&1 && set "DOCKER_AVAILABLE=1"

if "%DOCKER_AVAILABLE%"=="1" (
  call :launch_docker
) else (
  echo %WARN% Docker not available. Starting natively.
  call :launch_native
)

if errorlevel 1 (
  echo %FAIL% Startup failed. Check output above.
  pause
  exit /b 1
)

:: ---------- open browser ----------
timeout /t 3 /nobreak >nul
start "" "http://localhost:3002"
echo %PASS% Browser opened to http://localhost:3002

:: ---------- summary ----------
echo.
echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney is running%RESET%
echo %BOLD%======================================================%RESET%
echo.
echo   Frontend:     %CYAN%http://localhost:3002%RESET%
echo   Backend API:  %CYAN%http://localhost:8080/api/v1%RESET%
echo   Swagger Docs: %CYAN%http://localhost:8080/docs%RESET%
echo   Dashboard:    %CYAN%http://localhost:3002/app/dashboard%RESET%
echo   Login (demo): %CYAN%demo@example.com / password123%RESET%
echo.
echo %INFO% To stop: double-click scripts\stop-IntelliMoney.bat
echo %INFO% Or: docker compose down  (if using Docker)
echo.
echo %BOLD%Press any key to close this window...%RESET%
pause <nul >nul 2>&1
exit /b 0

:: ==================== SUBROUTINES ====================

:check_prereqs
where python >nul 2>&1 || (
  echo %FAIL% Python not found. Install from https://www.python.org/downloads/
  exit /b 1
)
where node >nul 2>&1 || (
  echo %FAIL% Node.js not found. Install from https://nodejs.org/
  exit /b 1
)
if not exist "%BACKEND_DIR%\.env" (
  if exist "%BACKEND_DIR%\.env.example" (
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    echo %WARN% Created .env from .env.example — edit SECRET_KEY and BANK_ENCRYPTION_KEY
  ) else (
    echo %FAIL% Missing backend\.env
    exit /b 1
  )
)
exit /b 0

:launch_docker
echo %INFO% Starting Docker Compose...
cd /d "%ROOT_DIR%"
docker compose up -d --remove-orphans 2>&1
if errorlevel 1 (
  echo %FAIL% Docker Compose failed to start.
  exit /b 1
)
echo %PASS% Docker containers starting.

:: poll backend health
set "WAITED=0"
:docker_wait
timeout /t 5 /nobreak >nul
set /a "WAITED+=5"
curl.exe -s -o nul -w "%%{http_code}" http://localhost:8080/healthz 2>nul | findstr "200" >nul
if !ERRORLEVEL! equ 0 (
  echo %PASS% Backend is responding.
  goto :docker_seed
)
if !WAITED! lss 45 goto docker_wait
echo %WARN% Backend health check timed out. Continuing anyway.
goto :docker_seed

:docker_seed
echo %INFO% Running demo seed...
docker compose run --rm seed 2>&1
echo %PASS% Demo seed complete.
exit /b 0

:launch_native
:: ---------- backend ----------
echo %BOLD%--- Backend ---%RESET%
cd /d "%BACKEND_DIR%"
set "VENV_DIR=%BACKEND_DIR%\venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
  echo %INFO% Creating Python virtual environment...
  python -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate.bat"
pip install -r requirements.txt --quiet 2>nul
echo %PASS% Python dependencies ready.

if not exist "%BACKEND_DIR%\uploads\receipts" mkdir "%BACKEND_DIR%\uploads\receipts"

:: run index & seed
"%VENV_DIR%\Scripts\python" "%ROOT_DIR%\scripts\create_indexes.py" 2>nul
"%VENV_DIR%\Scripts\python" "%ROOT_DIR%\backend\scripts\seed_demo.py" 2>nul

echo %INFO% Starting backend on port 8080...
start "IntelliMoney-Backend" cmd /c "title IntelliMoney Backend && cd /d "%BACKEND_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080"

:: poll
set "WAITED=0"
:backend_wait
timeout /t 3 /nobreak >nul
set /a "WAITED+=3"
curl.exe -s -o nul -w "%%{http_code}" http://localhost:8080/healthz 2>nul | findstr "200" >nul
if !ERRORLEVEL! equ 0 (
  echo %PASS% Backend is responding.
  goto :frontend_start
)
if !WAITED! lss 45 goto backend_wait
echo %WARN% Backend not yet responding — continuing.

:: ---------- frontend ----------
:frontend_start
echo %BOLD%--- Frontend ---%RESET%
cd /d "%FRONTEND_DIR%"
if not exist "%FRONTEND_DIR%\node_modules" (
  echo %INFO% Installing npm packages...
  call npm install 2>nul
  if errorlevel 1 (
    echo %FAIL% npm install failed.
    exit /b 1
  )
  echo %PASS% npm packages installed.
) else (
  echo %PASS% node_modules exists.
)

echo %INFO% Starting frontend on port 5173...
start "IntelliMoney-Frontend" cmd /c "title IntelliMoney Frontend && cd /d "%FRONTEND_DIR%" && npm run dev"

set "WAITED=0"
:frontend_wait
timeout /t 3 /nobreak >nul
set /a "WAITED+=3"
curl.exe -s -o nul -w "%%{http_code}" http://localhost:5173 2>nul | findstr "200 302" >nul
if !ERRORLEVEL! equ 0 (
  echo %PASS% Frontend is responding.
  exit /b 0
)
if !WAITED! lss 45 goto frontend_wait
echo %WARN% Frontend not yet responding — continuing.exit /b 0
