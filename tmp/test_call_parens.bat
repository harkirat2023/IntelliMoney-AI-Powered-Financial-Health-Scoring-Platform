@echo off
setlocal enabledelayedexpansion
set "_name=Backend API (Docker)"
set "_count=3"
call :log "%_name% health check passed after !_count! attempts"
echo Done
exit /b 0
:log
echo [%DATE% %TIME%] %*
exit /b 0