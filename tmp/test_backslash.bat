@echo off
setlocal enabledelayedexpansion
set "WARN=[WARN]"
if 1 equ 0 (
    echo True
) else (
    echo %WARN% WebSocket check failed. \(expected if not connected via WS\).
)
echo Done