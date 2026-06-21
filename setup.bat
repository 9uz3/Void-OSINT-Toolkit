@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title VOID-OSINT Setup

echo(
echo   VOID OSINT TOOLKIT - Installation
echo   ==================================
echo(

set "PYEXE="

if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python313\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python310\python.exe"

where py >nul 2>&1
if not errorlevel 1 if not defined PYEXE for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
if not defined PYEXE (
  where py >nul 2>&1
  if not errorlevel 1 for /f "delims=" %%P in ('py -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
)
where python >nul 2>&1
if not defined PYEXE for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
where python3 >nul 2>&1
if not defined PYEXE for /f "delims=" %%P in ('python3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"

if not defined PYEXE (
  echo(
  echo   [ERROR] Python not found.
  echo   Install Python 3.8+ : https://www.python.org/downloads/
  pause
  exit /b 1
)

"%PYEXE%" -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if errorlevel 1 (
  echo   [ERROR] Python 3.8+ required.
  "%PYEXE%" --version
  pause
  exit /b 1
)

if not exist "Void\main.py" (
  echo   [ERROR] Void folder not found. Run setup.bat from root.
  pause
  exit /b 1
)

if not exist "Void\requirements.txt" (
  echo   [ERROR] requirements.txt not found.
  pause
  exit /b 1
)

if not exist "Void\data" mkdir "Void\data"
if not exist "Void\config" mkdir "Void\config"

echo   Python detected :
"%PYEXE%" --version
echo(
echo   Installing dependencies...
"%PYEXE%" -m pip install --upgrade pip >nul 2>&1
"%PYEXE%" -m pip install -r "Void\requirements.txt"
if errorlevel 1 (
  echo(
  echo   [ERROR] Installation failed.
  pause
  exit /b 1
)

echo(
echo   OK - Dependencies installed.
echo   Launch Void-OSINT with start.bat
echo(
pause
exit /b 0
