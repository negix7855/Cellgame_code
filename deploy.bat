@echo off

echo ==============================
echo Copy
echo ==============================

robocopy build\web ..\github_upload\ /E

echo.

echo ==============================
echo Git Upload
echo ==============================

cd /d ..\github_upload

git add .
git commit -m "update %date% %time%"
git push

echo.
echo ==============================
echo done
echo ==============================

pause
