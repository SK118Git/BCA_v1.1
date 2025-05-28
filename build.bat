@echo off
REM Windows build script for BCA 

echo 🔨 Building BCA executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Install build dependencies if needed
echo 📦 Installing build dependencies...
pip install -e ".[build]" >nul 2>&1

REM Run the build script
echo 🚀 Starting build process...
python build.py

REM Check if build was successful
if exist "dist\BCA_Tool.exe" (
    echo.
    echo ✅ Build completed successfully!
    echo 📁 Executable created: dist\BCA_Tool.exe
    echo.
    echo Would you like to test the executable? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Testing executable...
        dist\BCA_Tool.exe
    )
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause