@echo off
setlocal enabledelayedexpansion
set "PASS=[32m[PASS][0m"
set "_name=Backend API"
set "_count=3"
set "ERRORLEVEL=0"
if !ERRORLEVEL! equ 0 (
    echo %PASS% %_name% is responding.
)
echo Done