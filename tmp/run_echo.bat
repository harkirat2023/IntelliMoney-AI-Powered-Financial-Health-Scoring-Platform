@echo off
setlocal enabledelayedexpansion

:: Can't use echo on this way, but let's try running with ECHO ON
cmd /v /c "echo on & ""D:\1. PLACEMENT\IntelliMoney\scripts\start-IntelliMoney.bat""" 2>&1 | Select-Object -First 50