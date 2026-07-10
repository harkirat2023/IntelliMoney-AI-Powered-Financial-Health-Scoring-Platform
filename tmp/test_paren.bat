@echo off
setlocal enabledelayedexpansion
set "WARN=[WARN]"
if 1 equ 0 (
    echo True branch
) else (
    echo %WARN% WebSocket check failed. (expected if not connected)
    echo %WARN% WebSocket check failed. (expected)
)
echo Done