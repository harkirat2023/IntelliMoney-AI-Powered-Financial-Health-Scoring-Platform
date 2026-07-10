@echo off
setlocal enabledelayedexpansion
echo Testing timeout...
timeout /t 2 /nobreak <nul >nul
echo Done