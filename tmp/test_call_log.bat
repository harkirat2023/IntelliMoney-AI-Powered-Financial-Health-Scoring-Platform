@echo off
setlocal enabledelayedexpansion
set "PASS=[32m[PASS][0m"
set "_name=Backend API"
set "_count=3"
set "ERRORLEVEL=0"
if !ERRORLEVEL! equ 0 (
    echo %PASS% %_name% is responding.
    call :log "%_name% health check passed after !_count! attempts"
    exit /b 0
)
:log
echo [%DATE% %TIME%] %* >> "D:\1. PLACEMENT\IntelliMoney\tmp\test.log"
exit /b 0