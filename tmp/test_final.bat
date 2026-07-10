@echo off
setlocal enabledelayedexpansion
set "WARN=[WARN]"
if 1 equ 0 (
    echo True
) else (
    echo %WARN% Test (expected)
    echo %WARN% Test (expected) after
)
echo Done