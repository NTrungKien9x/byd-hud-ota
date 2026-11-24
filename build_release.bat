@echo off
chcp 65001 >nul
python "%~dp0build_release.py"
pause
