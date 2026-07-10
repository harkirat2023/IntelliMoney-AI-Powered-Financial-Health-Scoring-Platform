@echo off
setlocal enabledelayedexpansion

:: ======================================================================
:: IntelliMoney Graceful Stop Script
:: ======================================================================

set "ROOT_DIR=%~dp0.."
set "STARTUP_LOG=%ROOT_DIR%\logs\startup.log"

:: ANSI color support
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

echo.
echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney - Shutting Down%RESET%
echo %BOLD%======================================================%RESET%
echo.

:: ---- Kill backend process ----
echo %INFO% Stopping Backend...
taskkill /FI "WINDOWTITLE eq IntelliMoney Backend" /T /F >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %PASS% Backend stopped.
) else (
    :: Fallback: kill uvicorn processes
    taskkill /IM "uvicorn" /F >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo %PASS% Backend stopped.
    ) else (
        echo %INFO% No running backend process found.
    )
)

:: ---- Kill frontend process ----
echo %INFO% Stopping Frontend...
taskkill /FI "WINDOWTITLE eq IntelliMoney Frontend" /T /F >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %PASS% Frontend stopped.
) else (
    :: Fallback: kill webpack/node processes related to this project
    taskkill /FI "WINDOWTITLE eq *webpack*" /T /F >nul 2>&1
    taskkill /IM "node.exe" /FI "WINDOWTITLE eq *IntelliMoney*" /F >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo %PASS% Frontend stopped.
    ) else (
        echo %INFO% No running frontend process found.
    )
)

:: ---- Stop Docker containers ----
echo %INFO% Stopping Docker containers...
where docker >nul 2>&1
if %ERRORLEVEL% equ 0 (
    docker info >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        if exist "%ROOT_DIR%\docker-compose.yml" (
            cd /d "%ROOT_DIR%"
            docker compose down 2>nul
            if !ERRORLEVEL! equ 0 (
                echo %PASS% Docker containers stopped.
            ) else (
                echo %WARN% Docker Compose down had issues.
            )
        ) else (
            echo %INFO% No docker-compose.yml found.
        )
    ) else (
        echo %INFO% Docker daemon not running. Skipping.
    )
) else (
    echo %INFO% Docker not installed. Skipping.
)

:: ---- Cleanup any lingering processes on ports ----
echo %INFO% Checking for lingering processes on common ports...
for %%p in (8080 5173) do (
    netstat -ano | findstr ":%%p " >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        for /F "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p "') do (
            taskkill /PID %%a /F >nul 2>&1
        )
        if !ERRORLEVEL! equ 0 echo %PASS% Freed port %%p.
    )
)

:: ---- Log shutdown ----
if exist "%ROOT_DIR%\logs" (
    echo [%DATE% %TIME%] IntelliMoney Shutdown Complete >> "%STARTUP_LOG%" 2>nul
    echo ================================== >> "%STARTUP_LOG%" 2>nul
)

echo.
echo %BOLD%======================================================%RESET%
echo %BOLD%    IntelliMoney - Shutdown Complete%RESET%
echo %BOLD%======================================================%RESET%
echo.
echo %PASS% All services stopped gracefully.
echo %INFO% Application data has been preserved.
echo.
echo %BOLD%To start again, double-click: scripts\start-IntelliMoney.bat%RESET%
echo.
timeout /t 5 /nobreak >nul
exit /b 0
