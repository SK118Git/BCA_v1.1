@echo off
REM Windows build script for BCA 

echo Building BCA executable...
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check Python version >= 3.11
for /f "tokens=2 delims= " %%v in ('py --version') do set PY_VER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo Python 3.11 or higher is required!
    pause
    exit /b 1
)
if %MAJOR%==3 if %MINOR% LSS 11 (
    echo Python 3.11 or higher is required!
    pause
    exit /b 1
)

REM Create venv if not exists
if not exist "venv" (
    echo Creating virtual environment...
    py -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install build dependencies
echo Installing build dependencies...
python -m pip install .
if %errorlevel% neq 0 (
    echo Dependency installation failed!
    pause
    exit /b 1
)

REM Build
echo Starting build process...
python build.py

REM Check if build was successful
if exist "dist\BCA_Tool.exe" (
    echo.
    echo Build completed successfully!
    echo Executable created: dist\BCA_Tool.exe
    echo.
    set /p choice=Would you like to test the executable? (y/n): 
    if /i "%choice%"=="y" (
        echo Testing executable...
        dist\BCA_Tool.exe
    )
) else (
    echo.
    echo Build failed! Check the output above for errors.
)

echo.
pause
