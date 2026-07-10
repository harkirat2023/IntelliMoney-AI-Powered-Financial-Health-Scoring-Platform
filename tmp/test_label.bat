@echo off
setlocal enabledelayedexpansion
set "DOCKER_MODE=1"
if "%DOCKER_MODE%"=="1" (
    echo Inside if
    call :sub
    goto :mylabel
)
echo After if - should NOT print
:mylabel
echo At mylabel
exit /b 0
:sub
echo In subroutine
exit /b 0