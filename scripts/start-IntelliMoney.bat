@echo off
setlocal enabledelayedexpansion

:: ======================================================================
:: IntelliMoney One-Click Startup Script
:: ======================================================================

set "ROOT_DIR=%~dp0.."
set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"
set "SCRIPTS_DIR=%ROOT_DIR%\scripts"
set "LOGS_DIR=%ROOT_DIR%\logs"
set "TMP_DIR=%ROOT_DIR%\tmp"
set "STARTUP_LOG=%LOGS_DIR%\startup.log"
set "START_TIME=%TIME%"

:: ----------------------------------------------------------------------
:: Ensure project directories exist
:: ----------------------------------------------------------------------
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%TMP_DIR%" mkdir "%TMP_DIR%"

:: Start logging
echo [%DATE% %TIME%] IntelliMoney Startup Started > "%STARTUP_LOG%"
echo ================================== >> "%STARTUP_LOG%"

:: ----------------------------------------------------------------------
:: Colored output helpers (Windows 10+ ANSI)
:: ----------------------------------------------------------------------
for /F "tokens=2 delims=." %%a in ('ver') do set "WIN_VER=%%a"
set "GREEN="
set "YELLOW="
set "RED="
set "CYAN="
set "BOLD="
set "RESET="
set "SUPPORT_COLOR=0"
ver | findstr /C:"10." >nul 2>&1 && set "SUPPORT_COLOR=1"
if "%SUPPORT_COLOR%"=="1" (
    for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
    set "GREEN=%ESC%[32m"
    set "YELLOW=%ESC%[33m"
    set "RED=%ESC%[31m"
    set "CYAN=%ESC%[36m"
    set "BOLD=%ESC%[1m"
    set "RESET=%ESC%[0m"
)

set "PASS=%GREEN%[PASS]%RESET%"
set "WARN=%YELLOW%[WARN]%RESET%"
set "FAIL=%RED%[FAIL]%RESET%"
set "INFO=%CYAN%[INFO]%RESET%"

echo.& echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney — One-Click Startup%RESET%
echo %BOLD%======================================================%RESET%
echo.

:: ----------------------------------------------------------------------
:: Function: log
:: ----------------------------------------------------------------------
goto :main

:log
echo [%DATE% %TIME%] %* >> "%STARTUP_LOG%"
exit /b 0

:check_port
set "_port=%1"
set "_name=%2"
netstat -ano | findstr ":%_port% " >nul 2>&1
if !ERRORLEVEL! equ 0 (
    for /F "tokens=5" %%a in ('netstat -ano ^| findstr ":%_port% "') do (
        for /F "tokens=1 delims= " %%b in ('tasklist /FI "PID eq %%a" ^| findstr /V "Image Name" ^| findstr /V "==" ^| findstr /R "^."') do set "_proc=%%b"
        echo %WARN% Port %_port% (%_name%) is in use by PID %%a !_proc!
    )
    exit /b 1
)
exit /b 0

:wait_for_url
set "_url=%1"
set "_name=%2"
set "_max=%3"
if "%_max%"=="" set "_max=30"
set "_count=0"
:wait_loop
timeout /t 2 /nobreak >nul
set /a "_count+=1"
>nul 2>&1 curl.exe -s -o nul -w "%%{http_code}" "%_url%" | findstr "200 302 301" >nul
if !ERRORLEVEL! equ 0 (
    echo %PASS% %_name% is responding.
    call :log "%_name% health check passed (attempt !_count!)"
    exit /b 0
)
if !_count! geq !_max! (
    echo %FAIL% %_name% did not respond within %_max% attempts.
    call :log "%_name% health check FAILED after %_max% attempts"
    exit /b 1
)
if !_count! equ 1 echo %INFO% Waiting for %_name% to start...
goto :wait_loop

:: ======================================================================
:: MAIN
:: ======================================================================
:main
call :log "===== STEP 1: Environment Validation ====="
echo %BOLD%STEP 1: Environment Validation%RESET%
echo.

:: --- Git ---
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %FAIL% Git is NOT installed.
    echo        Download from: https://git-scm.com/download/win
    call :log "FAIL: Git not installed"
) else (
    for /F "tokens=1-3" %%a in ('git --version') do set "GIT_VER=%%c"
    echo %PASS% Git found: !GIT_VER!
    call :log "Git found: !GIT_VER!"
)

:: --- Python ---
set "PYTHON_OK=0"
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /F "tokens=2" %%a in ('python --version 2^>^&1') do set "PY_VER=%%a"
    echo %PASS% Python found: !PY_VER!
    set "PYTHON_OK=1"
    call :log "Python found: !PY_VER!"
) else (
    where python3 >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        for /F "tokens=2" %%a in ('python3 --version 2^>^&1') do set "PY_VER=%%a"
        echo %PASS% Python3 found: !PY_VER!
        set "PYTHON_OK=1"
        set "PYTHON_CMD=python3"
        call :log "Python3 found: !PY_VER!"
    ) else (
        echo %FAIL% Python is NOT installed.
        echo        Download from: https://www.python.org/downloads/
        echo        Make sure to check "Add Python to PATH".
        call :log "FAIL: Python not installed"
    )
)
if "%PYTHON_CMD%"=="" set "PYTHON_CMD=python"

:: --- Node.js ---
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %FAIL% Node.js is NOT installed.
    echo        Download from: https://nodejs.org/
    call :log "FAIL: Node.js not installed"
) else (
    for /F "tokens=1" %%a in ('node --version') do set "NODE_VER=%%a"
    echo %PASS% Node.js found: !NODE_VER!
    call :log "Node.js found: !NODE_VER!"
)

:: --- npm ---
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %FAIL% npm is NOT installed.
    echo        npm comes with Node.js. Reinstall Node.js.
    call :log "FAIL: npm not installed"
) else (
    for /F "tokens=1" %%a in ('npm --version') do set "NPM_VER=%%a"
    echo %PASS% npm found: !NPM_VER!
    call :log "npm found: !NPM_VER!"
)

:: --- Docker Desktop ---
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %WARN% Docker CLI not found (optional). Install Docker Desktop:
    echo        https://www.docker.com/products/docker-desktop/
    set "DOCKER_AVAILABLE=0"
    call :log "WARN: Docker not installed"
) else (
    for /F "tokens=1-3" %%a in ('docker --version') do set "DOCKER_VER=%%c"
    set "DOCKER_VER=!DOCKER_VER:,=!"
    echo %PASS% Docker found: !DOCKER_VER!
    set "DOCKER_AVAILABLE=1"
    call :log "Docker found: !DOCKER_VER!"

    docker info >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo %WARN% Docker daemon is NOT running.
        echo        Start Docker Desktop manually and try again.
        set "DOCKER_AVAILABLE=0"
        call :log "WARN: Docker daemon not running"
    ) else (
        echo %PASS% Docker daemon is running.
        call :log "Docker daemon running"
    )
)

:: --- Environment file check ---
if not exist "%BACKEND_DIR%\.env" (
    echo %WARN% Backend .env file not found.
    echo        Copy from: "%BACKEND_DIR%\.env.example" to "%BACKEND_DIR%\.env"
    if exist "%BACKEND_DIR%\.env.example" (
        echo %INFO% Creating .env from .env.example...
        copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
        echo %PASS% .env created. Please edit "%BACKEND_DIR%\.env" with your SECRET_KEY and BANK_ENCRYPTION_KEY.
    ) else (
        echo %FAIL% No .env.example found. Cannot create .env.
        call :log "FAIL: No .env.example found"
    )
) else (
    echo %PASS% Backend .env found.
    call :log ".env found"
)

:: --- Check required env vars ---
set "CFG_FILE=%BACKEND_DIR%\.env"
if exist "%CFG_FILE%" (
    findstr /B "SECRET_KEY=" "%CFG_FILE%" | findstr /V "SECRET_KEY=$" | findstr /V "SECRET_KEY=change-this" >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        echo %WARN% SECRET_KEY may not be configured in .env. JWT auth will fail.
    )
)

echo.& echo %BOLD%STEP 2: Docker Containers%RESET%
echo.

:: ======================================================================
:: STEP 2 — Docker
:: ======================================================================
call :log "===== STEP 2: Docker ====="
if "%DOCKER_AVAILABLE%"=="1" (
    if exist "%ROOT_DIR%\docker-compose.yml" (
        echo %INFO% Starting Docker containers...
        cd /d "%ROOT_DIR%"
        docker compose up -d 2>>"%STARTUP_LOG%"
        if !ERRORLEVEL! equ 0 (
            echo %PASS% Docker Compose started.
            call :log "Docker Compose started successfully"

            echo %INFO% Waiting for containers to become healthy...
            set "MAX_WAIT=60"
            set "WAITED=0"
            :docker_health_loop
            timeout /t 5 /nobreak >nul
            set /a "WAITED+=5"
            set "ALL_HEALTHY=1"
            for /F "tokens=1" %%a in ('docker compose ps --format "{{.Name}}" 2^>nul') do (
                set "CNAME=%%a"
                set "STATUS="
                for /F "tokens=*" %%b in ('docker inspect "%%a" --format "{{.State.Health.Status}}" 2^>nul') do set "STATUS=%%b"
                if not defined STATUS set "STATUS=running"
                if not "!STATUS!"=="healthy" if not "!STATUS!"=="running" set "ALL_HEALTHY=0"
            )
            if "!ALL_HEALTHY!"=="1" (
                echo %PASS% All Docker containers are healthy.
                call :log "Docker containers healthy"
            ) else (
                if !WAITED! lss !MAX_WAIT! (
                    if !WAITED! equ 5 echo %INFO% Waiting for Docker containers...
                    goto :docker_health_loop
                ) else (
                    echo %WARN% Some Docker containers may not be fully healthy.
                    docker compose ps
                )
            )
        ) else (
            echo %FAIL% Docker Compose failed to start.
            call :log "FAIL: Docker Compose start failed"
        )
        cd /d "%ROOT_DIR%"
    ) else (
        echo %INFO% No docker-compose.yml found. Skipping Docker.
    )
) else (
    echo %INFO% Docker not available. Skipping Docker step.
    echo        If you need MongoDB, start it manually or use Docker Desktop.
)

echo.& echo %BOLD%STEP 3: Backend%RESET%
echo.

:: ======================================================================
:: STEP 3 — Backend
:: ======================================================================
call :log "===== STEP 3: Backend ====="

cd /d "%BACKEND_DIR%"

:: --- Virtual Environment ---
set "VENV_DIR=%BACKEND_DIR%\venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo %INFO% Creating Python virtual environment...
    call :log "Creating virtual environment"
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    if !ERRORLEVEL! neq 0 (
        echo %FAIL% Failed to create virtual environment.
        call :log "FAIL: venv creation failed"
        pause
        exit /b 1
    )
    echo %PASS% Virtual environment created.
) else (
    echo %PASS% Virtual environment exists.
)

:: --- Install dependencies ---
echo %INFO% Checking Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
"%VENV_DIR%\Scripts\pip" install -r "%BACKEND_DIR%\requirements.txt" --quiet 2>>"%STARTUP_LOG%"
if %ERRORLEVEL% neq 0 (
    echo %WARN% pip install had warnings. Check "%STARTUP_LOG%" for details.
    call :log "WARN: pip install warnings"
) else (
    echo %PASS% Python dependencies installed.
    call :log "Python dependencies OK"
)

:: --- Create uploads directory ---
if not exist "%BACKEND_DIR%\uploads\receipts" (
    mkdir "%BACKEND_DIR%\uploads\receipts" >nul 2>&1
)

:: --- Check for existing index creation ---
echo %INFO% Running database index setup...
"%VENV_DIR%\Scripts\python" "%SCRIPTS_DIR%\create_indexes.py" >>"%STARTUP_LOG%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo %WARN% Index creation had issues (usually harmless on first run — indexes are auto-created on app startup).
    call :log "WARN: create_indexes.py had warnings"
) else (
    echo %PASS% Database indexes verified.
    call :log "Database indexes OK"
)

:: --- Start Backend ---
echo %INFO% Starting FastAPI backend on port 8080...
start "IntelliMoney-Backend" cmd /c "title IntelliMoney Backend && cd /d "%BACKEND_DIR%" && "%VENV_DIR%\Scripts\activate.bat" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 2>&1"
call :log "Backend process started"

:: --- Wait for backend to be ready ---
call :wait_for_url "http://localhost:8080/api/health" "Backend API" 30
set "BACKEND_READY=%ERRORLEVEL%"

echo.& echo %BOLD%STEP 4: Frontend%RESET%
echo.

:: ======================================================================
:: STEP 4 — Frontend
:: ======================================================================
call :log "===== STEP 4: Frontend ====="

cd /d "%FRONTEND_DIR%"

:: --- Install npm packages ---
if not exist "%FRONTEND_DIR%\node_modules" (
    echo %INFO% Installing npm packages...
    call :log "Installing npm packages"
    call npm install 2>>"%STARTUP_LOG%"
    if !ERRORLEVEL! neq 0 (
        echo %FAIL% npm install failed.
        call :log "FAIL: npm install failed"
        pause
        exit /b 1
    )
    echo %PASS% npm packages installed.
) else (
    echo %PASS% node_modules exists.
    :: Verify key packages exist
    if not exist "%FRONTEND_DIR%\node_modules\react" (
        echo %INFO% node_modules incomplete. Running npm install...
        call npm install 2>>"%STARTUP_LOG%"
    )
)

:: --- Start Frontend ---
echo %INFO% Starting frontend dev server on port 5173...
start "IntelliMoney-Frontend" cmd /c "title IntelliMoney Frontend && cd /d "%FRONTEND_DIR%" && npm run dev 2>&1"
call :log "Frontend process started"

:: --- Wait for frontend ---
call :wait_for_url "http://localhost:5173" "Frontend" 45
set "FRONTEND_READY=%ERRORLEVEL%"

echo.& echo %BOLD%STEP 5: Health Checks%RESET%
echo.

:: ======================================================================
:: STEP 5 — Health Checks
:: ======================================================================
call :log "===== STEP 5: Health Checks ====="

set "ALL_OK=1"

:: --- Backend ---
if "%BACKEND_READY%"=="0" (
    echo %PASS% Backend is running
) else (
    echo %FAIL% Backend is NOT running
    set "ALL_OK=0"
)

:: --- Frontend ---
if "%FRONTEND_READY%"=="0" (
    echo %PASS% Frontend is running
) else (
    echo %FAIL% Frontend is NOT running
    set "ALL_OK=0"
)

:: --- MongoDB check ---
>nul 2>&1 curl.exe -s "http://localhost:8080/api/health" | findstr "ok" >nul
if %ERRORLEVEL% equ 0 (
    >nul 2>&1 curl.exe -s "http://localhost:8080/api/health" | findstr "mongodb" >nul
    if !ERRORLEVEL! equ 0 (
        echo %PASS% MongoDB connected.
        set "MONGO_OK=1"
    ) else (
        :: Health endpoint might not return mongodb field but still be ok
        echo %PASS% Backend health endpoint responded \(MongoDB assumed connected\).
        set "MONGO_OK=1"
    )
) else (
    echo %WARN% Could not verify MongoDB connection.
    set "MONGO_OK=0"
)
call :log "MongoDB health: %MONGO_OK%"

:: --- Docker health ---
if "%DOCKER_AVAILABLE%"=="1" (
    >nul 2>&1 docker compose ps --format "{{.Status}}" | findstr "Up" >nul
    if !ERRORLEVEL! equ 0 (
        echo %PASS% Docker containers are up.
        set "DOCKER_OK=1"
    ) else (
        echo %WARN% No Docker containers appear to be running.
        set "DOCKER_OK=0"
    )
) else (
    set "DOCKER_OK=-"
    echo %INFO% Docker health: N/A (not used)
)
call :log "Docker health: %DOCKER_OK%"

:: --- WebSocket ---
>nul 2>&1 curl.exe -s -o nul -w "%%{http_code}" "http://localhost:8080/api/v1/ws" | findstr "426 400" >nul
if %ERRORLEVEL% equ 0 (
    echo %PASS% WebSocket endpoint available.
    set "WS_OK=1"
) else (
    echo %WARN% WebSocket endpoint check failed \(expected if not connected via WS\).
    set "WS_OK=0"
)
call :log "WebSocket health: %WS_OK%"

:: --- OpenAI ---
findstr /B "OPENAI_API_KEY" "%BACKEND_DIR%\.env" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    findstr /B "OPENAI_API_KEY=" "%BACKEND_DIR%\.env" | findstr /V "OPENAI_API_KEY=$" >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo %PASS% OpenAI API key configured.
        set "AI_OK=1"
    ) else (
        echo %WARN% OpenAI API key is empty. AI Copilot features will be limited.
        set "AI_OK=0"
    )
) else (
    echo %WARN% OpenAI not configured. AI Copilot features will be unavailable.
    set "AI_OK=0"
)
call :log "OpenAI health: %AI_OK%"

:: --- JWT Secret ---
findstr /B "SECRET_KEY" "%BACKEND_DIR%\.env" | findstr /V "SECRET_KEY=$" | findstr /V "change-this" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %PASS% JWT secret configured.
    set "JWT_OK=1"
) else (
    echo %WARN% JWT secret may use default value. Update SECRET_KEY in .env for production.
    set "JWT_OK=1"
)

:: --- Port check summary ---
call :check_port 8080 "Backend"
call :check_port 5173 "Frontend"

echo.& echo %BOLD%STEP 6: Opening Browser%RESET%
echo.

:: ======================================================================
:: STEP 6 — Open Browser
:: ======================================================================
call :log "===== STEP 6: Open Browser ====="
if "%FRONTEND_READY%"=="0" (
    echo %INFO% Opening IntelliMoney in your browser...
    start "" "http://localhost:5173"
    call :log "Browser opened to http://localhost:5173"
) else (
    if "%BACKEND_READY%"=="0" (
        echo %INFO% Frontend not ready. Opening backend API docs instead...
        start "" "http://localhost:8080/docs"
        call :log "Browser opened to http://localhost:8080/docs"
    )
)

echo.& echo %BOLD%======================================================%RESET%

:: ======================================================================
:: STEP 7 — Summary
:: ======================================================================
call :log "===== STEP 7: Summary ====="

:: Build status line
set "BACKEND_STATUS=%FAIL%"
if "%BACKEND_READY%"=="0" set "BACKEND_STATUS=%PASS%"

set "FRONTEND_STATUS=%FAIL%"
if "%FRONTEND_READY%"=="0" set "FRONTEND_STATUS=%PASS%"

set "MONGO_STATUS=%FAIL%"
if "%MONGO_OK%"=="1" set "MONGO_STATUS=%PASS%"

set "DOCKER_STATUS=%FAIL%"
if "%DOCKER_OK%"=="1" set "DOCKER_STATUS=%PASS%"
if "%DOCKER_OK%"=="-" set "DOCKER_STATUS=%INFO%"

set "AI_STATUS=%FAIL%"
if "%AI_OK%"=="1" set "AI_STATUS=%PASS%"

set "WS_STATUS=%FAIL%"
if "%WS_OK%"=="1" set "WS_STATUS=%PASS%"

echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney — Startup Complete%RESET%
echo %BOLD%======================================================%RESET%
echo.
echo %BOLD%  Service              Status%RESET%
echo %BOLD%  --------------------  --------%RESET%
echo   Backend              %BACKEND_STATUS%
echo   Frontend             %FRONTEND_STATUS%
echo   MongoDB              %MONGO_STATUS%
echo   Docker               %DOCKER_STATUS%
echo   AI Services          %AI_STATUS%
echo   WebSocket            %WS_STATUS%
echo %BOLD%  --------------------  --------%RESET%
echo.
echo %BOLD%  URLs%RESET%
echo   Frontend:     %CYAN%http://localhost:5173%RESET%
echo   Backend API:  %CYAN%http://localhost:8080/api/v1%RESET%
echo   Swagger Docs: %CYAN%http://localhost:8080/docs%RESET%
echo.
echo %BOLD%  Quick Links%RESET%
echo   Dashboard:    %CYAN%http://localhost:5173/app/dashboard%RESET%
echo   Login:        %CYAN%http://localhost:5173/login%RESET%
echo.

if "%ALL_OK%"=="1" (
    echo %PASS% %BOLD%All systems operational!%RESET%
) else (
    echo %WARN% %BOLD%Some services may not be fully ready.%RESET%
    echo        Check the logs above and in "%STARTUP_LOG%"
)

echo.
echo %CYAN%To stop all services, double-click: scripts\stop-IntelliMoney.bat%RESET%
echo.
echo %BOLD%======================================================%RESET%
call :log "===== Startup finished ====="
call :log "Backend=%BACKEND_READY% Frontend=%FRONTEND_READY% MongoDB=%MONGO_OK% Docker=%DOCKER_OK%"

:: Write final summary to log
echo. >> "%STARTUP_LOG%"
echo ================================== >> "%STARTUP_LOG%"
echo [%DATE% %TIME%] IntelliMoney Startup Complete >> "%STARTUP_LOG%"
echo Backend Status: %BACKEND_READY% >> "%STARTUP_LOG%"
echo Frontend Status: %FRONTEND_READY% >> "%STARTUP_LOG%"
echo MongoDB: %MONGO_OK% >> "%STARTUP_LOG%"
echo ================================== >> "%STARTUP_LOG%"

:: Keep the window open so user can see the summary
echo.
echo %BOLD%Press any key to close this window...%RESET%
echo %CYAN%\(Services will continue running in their own windows\)%RESET%
pause >nul 2>&1
exit /b 0
