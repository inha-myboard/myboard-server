@echo off
set MYBOARD_ENV=%1
IF NOT DEFINED MYBOARD_ENV set "MYBOARD_ENV=local"
set MYBOARD_SETTINGS=%CD%/%MYBOARD_ENV%.cfg
python myboard_server.py