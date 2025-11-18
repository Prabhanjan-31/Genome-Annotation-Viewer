@echo off
echo ===============================
echo   Starting Genome Viewer App
echo ===============================

REM Change directory to project folder
cd /d C:\Users\shali\Desktop\genome_viewer

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Running Streamlit app...
python -m streamlit run app.py

echo.
echo Streamlit app closed.
pause
