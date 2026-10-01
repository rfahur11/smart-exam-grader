@echo off
title Smart Exam Grader - MA Salafiyah Bantarsari
cd /d "%~dp0"

echo ========================================================
echo   Smart Exam Grader & AnBuso Auto-Filler
echo   MA Salafiyah Bantarsari
echo ========================================================
echo.

:: 1. Cek apakah Python terinstall
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python belum terinstall atau belum masuk ke PATH!
    echo Silakan install Python 3.10 atau 3.11 dari python.org
    echo Pastikan centang "Add python.exe to PATH" saat instalasi.
    echo.
    pause
    exit /b
)

:: 2. Setup Virtual Environment otomatis jika belum ada
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Menyiapkan environment pertama kali... Ini hanya berjalan sekali.
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Menginstall dependensi (Streamlit, OpenCV, RapidOCR, pywin32)...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [INFO] Setup selesai!
    echo.
) else (
    call .venv\Scripts\activate.bat
)

:: 3. Jalankan aplikasi Streamlit
echo [INFO] Membuka dashboard antarmuka guru...
start http://localhost:8501
streamlit run app.py --server.headless false --server.port 8501

pause

