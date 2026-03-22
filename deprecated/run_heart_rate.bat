@echo off
echo Fetching latest heart rate data...
python get_latest_heart_rate.py > heart_rate_log.txt 2>&1
if exist heart_rate_log.txt (
    type heart_rate_log.txt
    echo.
    echo Output has been saved to heart_rate_log.txt
) else (
    echo Error: Could not capture output
)
pause
