@echo off
echo Fetching ALL historical heart rate data...
python get_all_heart_rate.py > heart_rate_full_log.txt 2>&1
if exist all_heart_rate_data.csv (
    echo.
    echo Data has been saved to all_heart_rate_data.csv
    echo.
    echo First 5 entries:
    echo -------------------
    powershell -command "& {Get-Content all_heart_rate_data.csv -Head 6}"
    echo.
    echo Full log saved to heart_rate_full_log.txt
) else (
    echo Error: Could not fetch heart rate data
    echo Check heart_rate_full_log.txt for details
)
pause
