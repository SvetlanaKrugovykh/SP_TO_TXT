@echo off
setlocal enabledelayedexpansion
cd /d C:\intelligence\SP_TO_TXT

REM Set UTF-8 encoding for Python output
set PYTHONIOENCODING=utf-8

REM Redirect all output to log file
(
  echo Starting FastWhisper Service at %date% %time%
  echo Working directory: %cd%
  
  echo Running: C:\intelligence\SP_TO_TXT\venv\Scripts\python.exe src\app.py
  C:\intelligence\SP_TO_TXT\venv\Scripts\python.exe src\app.py
) >> "C:\logs\FastWhisper\service.log" 2>&1
