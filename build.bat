@echo off
setlocal
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
set PIP=.venv\Scripts\pip.exe

if not exist "%PYTHON%" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create venv. Is Python installed?
        exit /b 1
    )
)

echo Installing build dependencies...
"%PIP%" install -q pyinstaller pillow
if errorlevel 1 exit /b 1

echo Building StickerGoblin.exe...
"%PYTHON%" -m PyInstaller StickerGoblin.spec
if errorlevel 1 exit /b 1

if not exist "dist\StickerGoblin.exe" (
    echo Build failed: dist\StickerGoblin.exe not found.
    exit /b 1
)

echo Copying to project root...
copy /Y "dist\StickerGoblin.exe" "StickerGoblin.exe" >nul
if errorlevel 1 exit /b 1

echo.
echo Done! Upload this file to GitHub Releases:
echo   %CD%\StickerGoblin.exe
endlocal
