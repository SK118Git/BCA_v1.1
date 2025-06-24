@echo off
setlocal

REM Windows build script for BCA 

echo Building BCA executable...
echo.


echo Fetching valid Python installation "(v >= 3.10)"
for /f "delims=" %%P in ('call .\prep\find_py.bat') do set "python_bin=%%P"

if "%python_bin%"=="1" (
    echo NO valid python executable found
    pause
    exit /b 1
)

if "%python_bin%"=="2" (
    echo Only valid executable has major version "< 3"
    pause
    exit /b 1
)

if "%python_bin%"=="3" (
    echo Only valid executable has minor version "< 10"
    pause
    exit /b 1
)


REM Create venv if not exists
if not exist "venv" (
    echo Creating virtual environment...
    %python_bin% -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install build dependencies

echo Purging cache
%python_bin% -m pip cache purge 

echo Installing build dependencies...
venv\Scripts\python.exe -m pip install ".[dependencies,build]"
if %errorlevel% neq 0 (
    echo Dependency installation failed!
    pause
    exit /b 1
)

REM Build
echo Starting build process...
venv\Scripts\python.exe build.py

echo.
pause
endlocal