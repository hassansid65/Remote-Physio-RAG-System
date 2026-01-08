@echo off
echo ========================================
echo Remote Physio System Startup
echo ========================================

echo.
echo 1. Starting Docker Services...
echo.

REM Check if Weaviate is running
docker ps | findstr "8080" >nul
if %errorlevel% neq 0 (
    echo Starting Weaviate...
    docker run -d -p 8080:8080 -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true semitechnologies/weaviate:latest
) else (
    echo Weaviate already running
)

REM Check if MongoDB is running
docker ps | findstr "27017" >nul
if %errorlevel% neq 0 (
    echo Starting MongoDB...
    docker run -d -p 27017:27017 --name mongodb mongo:latest
) else (
    echo MongoDB already running
)

echo.
echo 2. Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 3. Starting FastAPI Server...
echo.
echo The server will start on http://localhost:8002
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.app:app --host 0.0.0.0 --port 8002 --reload

pause
