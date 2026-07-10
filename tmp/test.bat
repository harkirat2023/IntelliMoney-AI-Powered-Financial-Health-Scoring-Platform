@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0.."
set "BACKEND_DIR=%ROOT_DIR%\backend"

set "GREEN="
set "YELLOW="
set "RED="
set "CYAN="
set "BOLD="
set "RESET="
set "SUPPORT_COLOR=0"
ver | findstr /C:"10." >nul 2>&1 && set "SUPPORT_COLOR=1"
set "PASS=%GREEN%[PASS]%RESET%"
set "WARN=%YELLOW%[WARN]%RESET%"
set "FAIL=%RED%[FAIL]%RESET%"
set "INFO=%CYAN%[INFO]%RESET%"

echo Starting test
where docker >nul 2>&1
echo ERRORLEVEL after where: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Docker not found
) else (
    for /F "tokens=1-3" %%a in ('docker --version') do set "DOCKER_VER=%%c"
    set "DOCKER_VER=!DOCKER_VER:,=!"
    echo Docker found: !DOCKER_VER!
)
echo Test completed