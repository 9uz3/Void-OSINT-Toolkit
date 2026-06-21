@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"

:: Add to PATH for current user
set "TARGET=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
echo Adding Void OSINT to PATH...

:: Create a cmd script in a PATH directory
set "LINK_DIR=%USERPROFILE%\AppData\Local\VoidOSINT"
if not exist "%LINK_DIR%" mkdir "%LINK_DIR%"

copy /Y "%SCRIPT_DIR%voidosint.bat" "%LINK_DIR%\voidosint.bat" >nul

:: Add to user PATH
for /f "skip=2 tokens=3*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%A %%B"
if "%USER_PATH%"=="" set "USER_PATH=%LINK_DIR%"
echo %USER_PATH% | find /i "%LINK_DIR%" >nul
if errorlevel 1 (
    setx PATH "%USER_PATH%;%LINK_DIR%" >nul
    echo [OK] Added to PATH. Restart terminal or log out/in.
) else (
    echo [OK] Already in PATH.
)

echo.
echo   ============================================
echo   VOID OSINT TOOLKIT - Installed!
echo   ============================================
echo.
echo   Run: voidosint
echo   First run will install all dependencies.
echo.
pause
