@echo off
setlocal enabledelayedexpansion
set "WARN=[WARN]"
if 1 equ 0 (echo True) else (
    echo %WARN% Test (parens). after
)
echo Done