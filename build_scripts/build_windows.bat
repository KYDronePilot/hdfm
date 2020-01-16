rem Build script for hdfm on Windows

rem Overridable vars
if not defined PYTHON set PYTHON=python37.exe

rem Local variables
set DIR=%~p0
set PROJECT_PATH=%DIR%..
set VENV=%PROJECT_PATH%\venv
set PIP=%VENV%\Scripts\pip.exe
set PYINSTALLER=%VENV%\Scripts\pyinstaller.exe
set REQUIREMENTS=%PROJECT_PATH%\requirements.txt
set BUILD=%PROJECT_PATH%\build
set DIST=%PROJECT_PATH%\dist
set SPEC=%PROJECT_PATH%\utils\pyinstaller_windows.spec

rem Create virtualenv if one does not exist
IF NOT EXIST %VENV% (
    %PYTHON% -m venv %VENV%
)

rem Install requirements
%PIP% install -r %REQUIREMENTS%

rem Delete PyInstaller build/dist dirs
if exist %BUILD% rmdir %BUILD%
if exist %DIST% rmdir %DIST%

rem Build with PyInstaller
%PYINSTALLER% %SPEC%
