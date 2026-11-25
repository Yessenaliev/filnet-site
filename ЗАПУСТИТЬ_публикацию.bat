@echo off
cd /d "%~dp0"
echo.
echo STEP 1. GitHub login. If you are already logged in, this step is skipped.
gh auth status >nul 2>&1
if errorlevel 1 goto login
goto publish

:login
echo.
echo A CODE of 8 characters will appear. Remember it, press Enter,
echo the browser will open: paste the code and press Authorize.
echo Then come back to this window.
echo.
gh auth login --hostname github.com --git-protocol https --web

:publish
gh auth setup-git >nul 2>&1
echo.
echo STEP 2. Publishing the site. Wait about one minute, do not press anything.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0publish_github.ps1' *>&1 | Tee-Object -FilePath '%~dp0log.txt'"
echo.
echo ===== If you see links above - done. If you see red text - tell me "done" in the chat. =====
echo You can close this window with the X. Do not paste anything here.
cmd /k
