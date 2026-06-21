@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title VOID-OSINT

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
  pause
  exit /b 1
)

"%PYEXE%" -u "Void\main.py"
if errorlevel 1 (
  echo(
  echo   [ERROR] Launch failed. Run setup.bat first.
  pause
  exit /b 1
)
exit /b 0
