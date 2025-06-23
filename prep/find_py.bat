@echo off
setlocal

for %%V in (3.15 3.14 3.13 3.12 3.11) do (
    py -%%V -c "exit()" >nul 2>&1
    if %errorlevel%==0 (
        echo Using Python %%V
        set PY_VER=%%V
        goto :found
    )
)

echo No Python >= 3.11 found!
exit /b 1