@echo off
setlocal enabledelayedexpansion
set "INFO=[INFO]"
set "DOCKER_MODE=1"
if "%DOCKER_MODE%"=="1" (
    echo %INFO% Test (parens) after text here.
)
echo Done