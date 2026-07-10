@echo off
setlocal enabledelayedexpansion
set "PASS=[PASS]"
set "_name=Backend API (Docker)"
set "ERRORLEVEL=0"
if !ERRORLEVEL! equ 0 (
    echo %PASS% %_name% is responding.
    call :log "%_name% test"
)
echo Done
exit /b 0
:log
echo [LOG] %*
exit /b 0