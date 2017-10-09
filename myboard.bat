@echo off
set ENV=%1
IF NOT DEFINED ENV set "ENV=local"
set MYBOARD_SETTINGS=%CD%/%ENV%.cfg
python index.py 