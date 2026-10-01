@echo off
title Smart Exam Grader - MA Salafiyah Bantarsari
cd /d "%~dp0"
echo ========================================================
echo Membuka Smart Exam Grader & AnBuso Auto-Filler...
echo ========================================================
start http://localhost:8501
streamlit run app.py --server.headless false --server.port 8501
pause
