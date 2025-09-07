title KanColleCap Build Script
@echo off
chcp 65001
cd %~dp0

echo.
echo [START EXE BUILDER]
if not defined PYTHON set PYTHON=python
if not defined VENV_DIR set "VENV_DIR=%~dp0venv"

set ERROR_REPORTING=FALSE

dir "%VENV_DIR%\Scripts\Python.exe"
if %ERRORLEVEL% == 0 goto :activate_venv

echo.
echo [CREATE VENV]
for /f "delims=" %%i in ('%PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME=%%i
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv "%VENV_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Unable to create venv in directory "%VENV_DIR%"
    exit /b
)

:activate_venv
echo.
echo [ACTIVATE VENV]
set PYTHON=%VENV_DIR%\Scripts\Python.exe
echo venv %PYTHON%

echo.
echo [UPGRADE PIP]
%PYTHON% -m pip install --upgrade pip

echo.
echo [INSTALL REQUIREMENTS]
%PYTHON% -m pip install --upgrade -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Unable to install requirements.
    exit /b
)

echo.
echo [BUILD EXE]
%PYTHON% -m PyInstaller app.py --onefile --noconsole --icon=icon.ico --add-data "config.json;." --add-data "icon.ico;."

if %ERRORLEVEL% neq 0 (
    echo.
    echo [Failed]
    echo Unable to build KanColleCap.exe.
    echo Please check the output for errors.
    echo.
) else (
    echo.
    echo [Completed]
    echo building KanColleCap.exe successfully.
    echo Please press any key to exit.
    echo.
)
pause