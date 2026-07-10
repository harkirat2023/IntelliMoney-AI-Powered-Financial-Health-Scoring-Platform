@echo off
setlocal enabledelayedexpansion
set "INFO=[INFO]"
set "DOCKER_MODE=1"
if "%DOCKER_MODE%"=="1" (
    echo %INFO% Frontend is running in Docker (nginx on port 80). Waiting for health check...
)
echo Done