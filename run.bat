@echo off
REM ============================================================================
REM WiFi Share - Batch Startup Script
REM Starts both HTTP server and WebSocket server, then opens the browser
REM ============================================================================

echo ============================================================
echo WiFi Share - Local File and Text Sharing
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation... OK
echo.

REM Check if websockets library is installed
python -c "import websockets" >nul 2>&1
if errorlevel 1 (
    echo [2/5] Installing websockets library...
    pip install websockets
    if errorlevel 1 (
        echo [ERROR] Failed to install websockets library!
        echo Please run: pip install websockets
        pause
        exit /b 1
    )
) else (
    echo [2/5] Checking websockets library... OK
)
echo.

REM Detect local IP address using Python
echo [3/5] Detecting local IP address...
for /f "delims=" %%i in ('python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()"') do set LOCAL_IP=%%i

if "%LOCAL_IP%"=="" (
    echo [WARNING] Could not detect IP address automatically
    set LOCAL_IP=127.0.0.1
)

echo Local IP Address: %LOCAL_IP%
echo.

REM Define ports
set HTTP_PORT=8000
set WS_PORT=8765

REM URLs for access
set HTTP_URL=http://%LOCAL_IP%:%HTTP_PORT%
set WS_URL=ws://%LOCAL_IP%:%WS_PORT%

echo [4/5] Starting servers...
echo.
echo   HTTP Server:   %HTTP_URL%
echo   WebSocket:     %WS_URL%
echo.

REM Start HTTP server in a new window (minimized)
start "HTTP Server - Port %HTTP_PORT%" /min python -m http.server %HTTP_PORT%

REM Give HTTP server a moment to start
timeout /t 2 /nobreak >nul

REM Start WebSocket server in a new window
start "WebSocket Server - Port %WS_PORT%" python server.py

REM Give WebSocket server a moment to start
timeout /t 2 /nobreak >nul

REM Open default browser
echo [5/5] Opening browser...
start "" "%HTTP_URL%"
echo.

echo ============================================================
echo Servers are running!
echo ============================================================
echo.
echo Desktop URL:  %HTTP_URL%
echo Mobile URL:   Scan the QR code in the browser
echo.
echo Press Ctrl+C in the server windows to stop the servers
echo.
echo ============================================================
echo.

REM Keep this window open to show information
echo This window can be closed. Servers are running in separate windows.
echo.
pause
