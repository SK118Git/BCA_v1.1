@echo off
setlocal enabledelayedexpansion


REM ERROR CODES:
REM 1: NO valid python executable found
REM 2: Only valid executable is has major version < 3
REM 3: Only valid executable has minor version < 10

REM Try py launcher 
where py >nul 2>&1
if !errorlevel! == 0 (
    goto :py_launcher_found
)


REM Try classic Python 
:classic 
where python >nul 2>&1 
if !errorlevel! == 0 (
    goto :python_classic_found
)

REM Neither Found 
REM echo Error: No valid Python executable found 
REM echo Please make sure you have installed Python 3.10+ and have added it to you %%PATH%% 
echo 1
pause 
exit /b 1 


REM Finding correct version of python to use if on py_launcher 
:py_launcher_found
for %%V in (3.15 3.14 3.13 3.12 3.11 3.10) do (
    py -%%V -c "exit()" >nul 2>&1
    if !errorlevel!==0 (
        REM echo Using Python %%V
        set PY_VER=%%V
        goto :result_py_launcher
    )
)

REM echo No Python >= 3.10 found on py launcher, trying classic!
goto :classic 


:python_classic_found
REM Check Python version >= 3.10
for /f "tokens=2 delims= " %%v in ('python --version') do set PY_VER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    REM echo Python 3.10 or higher is required!
    echo 2
    pause
    exit /b 1
)
if %MAJOR%==3 if %MINOR% LSS 10 (
    REM echo Python 3.10 or higher is required!
    echo 3
    pause
    exit /b 1
)

REM Return result for use by other functions 
echo python 
exit /b 1 

REM Return result for py_launncher
:result_py_launcher
echo py -%PY_VER%
exit /b 1 

endlocal 