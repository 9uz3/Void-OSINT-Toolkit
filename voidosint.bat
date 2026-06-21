@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "VOID_DIR=%SCRIPT_DIR%Void"
set "PYEXE="

:: ── Find Python ──
if exist "%LocalAppData%\Programs\Python\Python314\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python314\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python313\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python310\python.exe"

where py >nul 2>&1
if not errorlevel 1 if not defined PYEXE for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
if not defined PYEXE (
    where python >nul 2>&1
    if not errorlevel 1 for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
)

if not defined PYEXE (
    echo [ERROR] Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: ── First-run: install all dependencies ──
set "INSTALLED_FLAG=%VOID_DIR%\config\.deps_installed"

if not exist "%INSTALLED_FLAG%" (
    echo.
    echo   ============================================
    echo   VOID OSINT TOOLKIT - First Run Setup
    echo   ============================================
    echo.

    echo [*] Step 1/3: Installing Python packages...
    "%PYEXE%" -m pip install --upgrade pip -q 2>nul
    "%PYEXE%" -m pip install -q -r "%VOID_DIR%\requirements.txt"
    if errorlevel 1 (
        echo [!] Some packages failed, retrying with --break-system-packages...
        "%PYEXE%" -m pip install -q --break-system-packages -r "%VOID_DIR%\requirements.txt" 2>nul
    )
    echo [+] Python packages installed.

    echo.
    echo [*] Step 2/3: Installing OSINT CLI tools...

    :: theHarvester (from GitHub)
    echo     - theHarvester...
    "%PYEXE%" -m pip install -q "theHarvester @ git+https://github.com/laramies/theHarvester.git" 2>nul
    if errorlevel 1 (
        echo     [!] theHarvester install failed (optional tool)
    )

    :: maigret
    echo     - maigret...
    "%PYEXE%" -m pip install -q maigret 2>nul

    :: phoneinfoga
    echo     - phoneinfoga...
    "%PYEXE%" -m pip install -q phoneinfoga 2>nul

    :: h8mail
    echo     - h8mail...
    "%PYEXE%" -m pip install -q h8mail 2>nul

    :: user-scanner
    echo     - user-scanner...
    "%PYEXE%" -m pip install -q user-scanner 2>nul

    :: nexfil
    echo     - nexfil...
    "%PYEXE%" -m pip install -q nexfil 2>nul

    echo [+] OSINT tools installed.

    echo.
    echo [*] Step 3/3: Finalizing...
    if not exist "%VOID_DIR%\config" mkdir "%VOID_DIR%\config"
    echo done > "%INSTALLED_FLAG%"
    echo [+] Setup complete!
    echo.
)

:: ── Launch ──
"%PYEXE%" -u "%VOID_DIR%\main.py" %*
pause
exit /b 0
