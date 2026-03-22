@echo off
echo Running Google Fit Data Source Check...
python check_fit_data.py > fit_output.txt 2>&1
type fit_output.txt
pause
