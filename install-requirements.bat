@echo off
echo Installing required packages...
set packages=flask qrcode pillow pyqrcode
for %%p in (%packages%) do (
    echo Installing %%p...
    python -m pip install %%p
)
echo Installation(s) completed
pause
