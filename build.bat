@echo off
REM Windows build script for Excel Analyzer

echo 🔨 Building Excel Analyzer executable...
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
if exist "dist\ExcelAnalyzer.exe" (
    echo.
    echo ✅ Build completed successfully!
    echo 📁 Executable created: dist\ExcelAnalyzer.exe
    echo.
    echo Would you like to test the executable? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Testing executable...
        dist\ExcelAnalyzer.exe
    )
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause