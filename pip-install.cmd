@echo off
rem -----------------------------------------------------
rem install/update 3rd party applications with Python pip
rem 20171029 HenkA
rem -----------------------------------------------------
@echo on
python.exe -m pip install --upgrade pip
pip install -U -r requirements.txt
echo.
pause